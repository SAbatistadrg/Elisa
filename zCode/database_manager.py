import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re


class DatabaseManager:
    """
    Gerenciador de banco de dados local para registro de análises.
    Armazena informações de cada processamento de cluster com inputs e outputs.
    """
    
    def __init__(self, db_path: str = "anp_analysis.db"):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, db_path)
        self._create_database()
    
    def _create_database(self):
        """Cria o banco de dados e a tabela se não existirem."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verifica se a tabela existe e se tem a coluna numero_analise
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='analises'
        """)
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Verifica se a coluna numero_analise existe
            cursor.execute("PRAGMA table_info(analises)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'numero_analise' not in columns:
                # Precisa fazer migração
                print("⚠️  Detectada estrutura antiga do banco. Fazendo migração...")
                self._migrate_database(conn)
                print("✅ Migração concluída!")
                conn.close()
                return
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TIMESTAMP NOT NULL,
                nome_projeto TEXT NOT NULL,
                cluster TEXT NOT NULL,
                numero_analise INTEGER NOT NULL,
                input1_subamostra_nr REAL NOT NULL,
                input2_confiabilidade REAL NOT NULL,
                input3_subamostra_r REAL NOT NULL,
                input4_dmp REAL,
                input5_nmi REAL,
                output1_epm REAL,
                output2_mep REAL,
                output3_sm REAL,
                UNIQUE(nome_projeto, cluster, numero_analise)
            )
        """)
        
        # Cria índices para melhorar performance de consultas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nome_projeto 
            ON analises(nome_projeto)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cluster 
            ON analises(cluster)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cluster_numero 
            ON analises(nome_projeto, cluster, numero_analise)
        """)
        
        conn.commit()
        conn.close()
    
    def _migrate_database(self, conn):
        """Migra o banco de dados antigo para a nova estrutura com numero_analise."""
        cursor = conn.cursor()
        
        # Cria uma tabela temporária com a nova estrutura
        cursor.execute("""
            CREATE TABLE analises_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TIMESTAMP NOT NULL,
                nome_projeto TEXT NOT NULL,
                cluster TEXT NOT NULL,
                numero_analise INTEGER NOT NULL,
                input1_subamostra_nr REAL NOT NULL,
                input2_confiabilidade REAL NOT NULL,
                input3_subamostra_r REAL NOT NULL,
                input4_dmp REAL,
                input5_nmi REAL,
                output1_epm REAL,
                output2_mep REAL,
                output3_sm REAL,
                UNIQUE(nome_projeto, cluster, numero_analise)
            )
        """)
        
        # Copia os dados antigos calculando numero_analise
        cursor.execute("""
            INSERT INTO analises_new (
                id, data_hora, nome_projeto, cluster, numero_analise,
                input1_subamostra_nr, input2_confiabilidade, input3_subamostra_r,
                input4_dmp, input5_nmi, output1_epm, output2_mep, output3_sm
            )
            SELECT 
                id, data_hora, nome_projeto, cluster,
                ROW_NUMBER() OVER (PARTITION BY nome_projeto, cluster ORDER BY data_hora) as numero_analise,
                input1_subamostra_nr, input2_confiabilidade, input3_subamostra_r,
                input4_dmp, input5_nmi, output1_epm, output2_mep, output3_sm
            FROM analises
        """)
        
        # Remove a tabela antiga
        cursor.execute("DROP TABLE analises")
        
        # Renomeia a nova tabela
        cursor.execute("ALTER TABLE analises_new RENAME TO analises")
        
        # Recria os índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nome_projeto 
            ON analises(nome_projeto)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cluster 
            ON analises(cluster)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cluster_numero 
            ON analises(nome_projeto, cluster, numero_analise)
        """)
        
        conn.commit()
    
    @staticmethod
    def extract_project_name(window_title: str) -> str:
        """
        Extrai o nome do projeto do título da janela.
        
        Args:
            window_title: Título completo da janela (ex: "NP_BRK-AREA-1900* - SCENE 2025.1.0")
        
        Returns:
            Nome do projeto (ex: "NP_BRK-AREA-1900*")
        """
        match = re.search(r'^(.+?)\s*-\s*SCENE', window_title)
        if match:
            return match.group(1).strip()
        return window_title.strip()
    
    def _get_next_analysis_number(self, nome_projeto: str, cluster: str) -> int:
        """
        Obtém o próximo número de análise para um cluster específico.
        
        Args:
            nome_projeto: Nome do projeto
            cluster: Nome do cluster
        
        Returns:
            Próximo número de análise (1 se for a primeira)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(numero_analise) 
            FROM analises 
            WHERE nome_projeto = ? AND cluster = ?
        """, (nome_projeto, cluster))
        
        result = cursor.fetchone()
        conn.close()
        
        max_number = result[0] if result[0] is not None else 0
        return max_number + 1
    
    def insert_analysis(self, 
                       nome_projeto: str,
                       cluster: str,
                       input1: float,
                       input2: float,
                       input3: float,
                       input4: Optional[float] = None,
                       input5: Optional[float] = None,
                       output1: Optional[float] = None,
                       output2: Optional[float] = None,
                       output3: Optional[float] = None) -> int:
        """
        Insere uma nova análise no banco de dados.
        O número da análise é calculado automaticamente (incremental por cluster).
        
        Args:
            nome_projeto: Nome do projeto extraído do título
            cluster: Nome do cluster processado
            input1: Subamostra NR
            input2: Confiabilidade
            input3: Subamostra R
            input4: DMP (opcional)
            input5: NMI (opcional)
            output1: EPM (opcional)
            output2: MEP (opcional)
            output3: SM em % (opcional)
        
        Returns:
            Tupla (ID da análise inserida, número da análise)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_hora = datetime.now().isoformat()  # Converte para string ISO format
        
        # Obtém o próximo número de análise para este cluster
        numero_analise = self._get_next_analysis_number(nome_projeto, cluster)
        
        cursor.execute("""
            INSERT INTO analises (
                data_hora, nome_projeto, cluster, numero_analise,
                input1_subamostra_nr, input2_confiabilidade, input3_subamostra_r,
                input4_dmp, input5_nmi,
                output1_epm, output2_mep, output3_sm
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data_hora, nome_projeto, cluster, numero_analise,
              input1, input2, input3,
              input4, input5,
              output1, output2, output3))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return (analysis_id, numero_analise)
    
    def get_analysis_count_by_cluster(self, cluster: str, nome_projeto: str) -> int:
        """
        Retorna o total de análises de um cluster específico.
        
        Args:
            cluster: Nome do cluster
            nome_projeto: Nome do projeto
        
        Returns:
            Número total de análises do cluster
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM analises 
            WHERE cluster = ? AND nome_projeto = ?
        """, (cluster, nome_projeto))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def get_analysis_by_number(self, cluster: str, nome_projeto: str, numero_analise: int) -> Optional[Dict]:
        """
        Recupera uma análise específica pelo número da análise.
        
        Args:
            cluster: Nome do cluster
            nome_projeto: Nome do projeto
            numero_analise: Número da análise
        
        Returns:
            Dicionário com os dados da análise ou None se não encontrada
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analises 
            WHERE cluster = ? AND nome_projeto = ? AND numero_analise = ?
        """, (cluster, nome_projeto, numero_analise))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """
        Recupera uma análise específica pelo ID.
        
        Args:
            analysis_id: ID da análise
        
        Returns:
            Dicionário com os dados da análise ou None se não encontrada
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analises WHERE id = ?
        """, (analysis_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_analyses_by_project(self, nome_projeto: str) -> List[Dict]:
        """
        Recupera todas as análises de um projeto específico.
        
        Args:
            nome_projeto: Nome do projeto
        
        Returns:
            Lista de dicionários com as análises
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analises 
            WHERE nome_projeto = ?
            ORDER BY data_hora DESC
        """, (nome_projeto,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_analyses_by_cluster(self, cluster: str, nome_projeto: Optional[str] = None) -> List[Dict]:
        """
        Recupera todas as análises de um cluster específico.
        
        Args:
            cluster: Nome do cluster
            nome_projeto: Nome do projeto (opcional, para filtrar)
        
        Returns:
            Lista de dicionários com as análises
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if nome_projeto:
            cursor.execute("""
                SELECT * FROM analises 
                WHERE cluster = ? AND nome_projeto = ?
                ORDER BY data_hora DESC
            """, (cluster, nome_projeto))
        else:
            cursor.execute("""
                SELECT * FROM analises 
                WHERE cluster = ?
                ORDER BY data_hora DESC
            """, (cluster,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_latest_analysis(self, cluster: str, nome_projeto: str) -> Optional[Dict]:
        """
        Recupera a análise mais recente de um cluster em um projeto.
        
        Args:
            cluster: Nome do cluster
            nome_projeto: Nome do projeto
        
        Returns:
            Dicionário com a análise mais recente ou None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analises 
            WHERE cluster = ? AND nome_projeto = ?
            ORDER BY data_hora DESC
            LIMIT 1
        """, (cluster, nome_projeto))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_all_analyses(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Recupera todas as análises do banco.
        
        Args:
            limit: Limite de registros (opcional)
        
        Returns:
            Lista de dicionários com todas as análises
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if limit:
            cursor.execute("""
                SELECT * FROM analises 
                ORDER BY data_hora DESC
                LIMIT ?
            """, (limit,))
        else:
            cursor.execute("""
                SELECT * FROM analises 
                ORDER BY data_hora DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_cluster_history(self, cluster: str, nome_projeto: str, limit: int = 10) -> List[Dict]:
        """
        Recupera o histórico de análises de um cluster para análise de evolução.
        
        Args:
            cluster: Nome do cluster
            nome_projeto: Nome do projeto
            limit: Número máximo de registros históricos
        
        Returns:
            Lista de análises ordenadas da mais recente para a mais antiga
        """
        analyses = self.get_analyses_by_cluster(cluster, nome_projeto)
        return analyses[:limit]
    
    def delete_database(self):
        """Remove o arquivo do banco de dados completamente."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"Banco de dados removido: {self.db_path}")
            # Recria o banco vazio
            self._create_database()
            print("Novo banco de dados criado.")
    
    def delete_analysis_by_id(self, analysis_id: int) -> bool:
        """
        Remove uma análise específica pelo ID.
        
        Args:
            analysis_id: ID da análise
        
        Returns:
            True se removida com sucesso, False caso contrário
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM analises WHERE id = ?", (analysis_id,))
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def get_statistics(self, nome_projeto: Optional[str] = None) -> Dict:
        """
        Retorna estatísticas gerais do banco de dados.
        
        Args:
            nome_projeto: Filtrar por projeto específico (opcional)
        
        Returns:
            Dicionário com estatísticas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if nome_projeto:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_analises,
                    COUNT(DISTINCT cluster) as total_clusters,
                    AVG(output3_sm) as media_sm,
                    MIN(data_hora) as primeira_analise,
                    MAX(data_hora) as ultima_analise
                FROM analises
                WHERE nome_projeto = ?
            """, (nome_projeto,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_analises,
                    COUNT(DISTINCT cluster) as total_clusters,
                    COUNT(DISTINCT nome_projeto) as total_projetos,
                    AVG(output3_sm) as media_sm,
                    MIN(data_hora) as primeira_analise,
                    MAX(data_hora) as ultima_analise
                FROM analises
            """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total_analises': row[0],
                'total_clusters': row[1],
                'total_projetos': row[2] if not nome_projeto else None,
                'media_sm': round(row[2 if nome_projeto else 3], 2) if row[2 if nome_projeto else 3] else None,
                'primeira_analise': row[3 if nome_projeto else 4],
                'ultima_analise': row[4 if nome_projeto else 5]
            }
        return {}
    
    @staticmethod
    def _row_to_dict(row: Tuple) -> Dict:
        """Converte uma linha do banco em dicionário."""
        return {
            'id': row[0],
            'data_hora': row[1],
            'nome_projeto': row[2],
            'cluster': row[3],
            'numero_analise': row[4],
            'input1_subamostra_nr': row[5],
            'input2_confiabilidade': row[6],
            'input3_subamostra_r': row[7],
            'input4_dmp': row[8],
            'input5_nmi': row[9],
            'output1_epm': row[10],
            'output2_mep': row[11],
            'output3_sm': row[12]
        }


# Exemplo de uso
if __name__ == "__main__":
    # Inicializa o gerenciador
    db = DatabaseManager()
    
    # Extrai nome do projeto do título da janela
    window_title = "NP_BRK-AREA-1900* - SCENE 2025.1.0"
    project_name = DatabaseManager.extract_project_name(window_title)
    print(f"Nome do projeto: {project_name}")
    
    # Insere uma análise de exemplo
    analysis_id, numero = db.insert_analysis(
        nome_projeto=project_name,
        cluster="Cluster_01",
        input1=0.070,
        input2=0.2,
        input3=0.044,
        input4=1.5,
        input5=2.3,
        output1=0.85,
        output2=1.2,
        output3=95.5
    )
    print(f"Análise inserida com ID: {analysis_id}, Número: {numero}")
    
    # Insere mais análises para o mesmo cluster
    for i in range(3):
        analysis_id, numero = db.insert_analysis(
            nome_projeto=project_name,
            cluster="Cluster_01",
            input1=0.070 + i*0.01,
            input2=0.2,
            input3=0.044,
            output1=0.85 + i*0.05,
            output2=1.2,
            output3=95.5 - i*0.5
        )
        print(f"Análise {numero} inserida para Cluster_01")
    
    # Verifica total de análises do cluster
    total = db.get_analysis_count_by_cluster("Cluster_01", project_name)
    print(f"\nTotal de análises do Cluster_01: {total}")
    
    # Recupera análise específica por número
    analysis = db.get_analysis_by_number("Cluster_01", project_name, 1)
    print(f"\nAnálise #1 do Cluster_01: {analysis}")
    
    # Recupera todas as análises do projeto
    project_analyses = db.get_analyses_by_project(project_name)
    print(f"\nTotal de análises do projeto: {len(project_analyses)}")
    
    # Estatísticas
    stats = db.get_statistics()
    print(f"\nEstatísticas gerais: {stats}")
    
    # Para deletar o banco (descomentar se necessário)
    # db.delete_database()