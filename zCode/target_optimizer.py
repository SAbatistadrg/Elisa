# target_optimizer.py
import numpy as np
from typing import Tuple, List, Optional
from skopt import gp_minimize
from skopt.space import Real
from context import context
from database_manager import DatabaseManager
from context import context

class TargetOptimizer:
    """
    Otimizador Bayesiano para definir targets de input1 e input3.
    Maximiza output3_sm usando Gaussian Process Optimization.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Inicializa o otimizador.

        Args:
            db_manager: Instância do DatabaseManager (opcional, cria uma nova se não fornecida)
        """
        self.db = db_manager if db_manager else DatabaseManager()

        # Definições de ranges e passos
        self.x1_min = context.dinamic_inputs['x1'] #se 
        self.x1_max = 0.1
        self.x1_step = 0.005

        self.x3_min = context.dinamic_inputs['x3']
        self.x3_max = 0.1
        self.x3_step = 0.001

        # Critérios de parada
        self.target_threshold = 60.0  # Para quando output3 >= 95%
        context.set_criterio(60) # substituir tudo depois por isso
        self.max_iterations = 30

        # Pontos iniciais (4 cantos do espaço de busca)
        self.initial_points = [
            (self.x1_min, self.x3_min),  # (0.010, 0.001)
            (self.x1_min, self.x3_max),  # (0.010, 0.1)
            (self.x1_max, self.x3_min),  # (0.1, 0.001)
            (self.x1_max, self.x3_max),  # (0.1, 0.1)
        ]
        self.initial_point_index = 0

    def _round_to_step(self, value: float, step: float) -> float:
        """Arredonda valor para o múltiplo mais próximo do passo."""
        return round(value / step) * step

    def _get_history(self) -> Tuple[List[Tuple[float, float]], List[float]]:
        """
        Busca histórico de análises do cluster atual no banco de dados.

        Returns:
            Tupla com (lista de pontos (x1, x3), lista de valores output3)
        """
        if not context.is_configured():
            raise ValueError("Contexto não configurado. Use context.set_project() e context.set_cluster()")

        analyses = self.db.get_analyses_by_cluster(
            cluster=context.cluster,
            nome_projeto=context.nome_projeto
        )

        X = []
        y = []

        for analysis in analyses:
            if analysis['output3_sm'] is not None:
                X.append((
                    analysis['input1_subamostra_nr'],
                    analysis['input3_subamostra_r']
                ))
                y.append(analysis['output3_sm'])

        return X, y

    def _check_target_reached(self, y_values: List[float]) -> bool:
        """Verifica se algum valor já atingiu o threshold."""
        if not y_values:
            return False
        return max(y_values) >= self.target_threshold

    def _get_next_initial_point(self) -> Tuple[float, float, float]:
        """
        Retorna o próximo ponto inicial da sequência.

        Returns:
            Tupla (x1, x2, x3)
        """
        if self.initial_point_index >= len(self.initial_points):
            # Se já usou todos os pontos iniciais, retorna um aleatório
            x1 = np.random.uniform(self.x1_min, self.x1_max)
            x3 = np.random.uniform(self.x3_min, self.x3_max)
        else:
            x1, x3 = self.initial_points[self.initial_point_index]
            self.initial_point_index += 1

        x1 = self._round_to_step(x1, self.x1_step)
        x3 = self._round_to_step(x3, self.x3_step)
        x2 = context.static_inputs['x2']

        return x1, x2, x3

    def _optimize_with_bayesian(self, X_history: List[Tuple[float, float]], 
                                y_history: List[float]) -> Tuple[float, float]:
        """
        Executa otimização Bayesiana para sugerir próximo ponto.

        Args:
            X_history: Lista de pontos já testados [(x1, x3), ...]
            y_history: Lista de valores output3 correspondentes

        Returns:
            Tupla (x1, x3) sugerida
        """
        # Define espaço de busca
        space = [
            Real(self.x1_min, self.x1_max, name='x1'),
            Real(self.x3_min, self.x3_max, name='x3')
        ]

        # Função objetivo (negativa porque gp_minimize minimiza)
        def objective(params):
            # Esta função não será chamada, apenas usamos para estrutura
            return 0

        # Converte histórico para formato do scikit-optimize
        X_init = np.array(X_history)
        y_init = np.array([-y for y in y_history])  # Negativo porque minimiza

        # Executa otimização (apenas 1 iteração para sugerir próximo ponto)
        result = gp_minimize(
            objective,
            space,
            x0=X_init.tolist(),
            y0=y_init.tolist(),
            n_calls=1,
            n_initial_points=0,
            acq_func='EI',  # Expected Improvement
            random_state=42
        )

        # Pega o ponto sugerido
        x1_suggested, x3_suggested = result.x_iters[-1]

        # Arredonda para os passos corretos
        x1_suggested = self._round_to_step(x1_suggested, self.x1_step)
        x3_suggested = self._round_to_step(x3_suggested, self.x3_step)

        # Garante que está dentro dos limites
        x1_suggested = np.clip(x1_suggested, self.x1_min, self.x1_max)
        x3_suggested = np.clip(x3_suggested, self.x3_min, self.x3_max)

        return x1_suggested, x3_suggested

    def get_new_targets(self) -> Tuple[float, float, float]:
        """
        Retorna os próximos targets otimizados (x1, x2, x3).

        Returns:
            Tupla (input1, input2, input3)

        Raises:
            ValueError: Se contexto não estiver configurado
            RuntimeError: Se atingir máximo de iterações sem sucesso
        """
        if not context.is_configured():
            raise ValueError(
                "Contexto não configurado. Configure com:\n"
                "  context.set_project(nome)\n"
                "  context.set_cluster(cluster)\n"
                "  context.set_static_inputs(x2, x4, x5)"
            )

        # Busca histórico
        X_history, y_history = self._get_history()

        # Verifica se já atingiu o threshold
        if self._check_target_reached(y_history):
            print(f"✅ Threshold de {self.target_threshold}% já atingido!")
            # Retorna o melhor ponto encontrado
            best_idx = np.argmax(y_history)
            x1_best, x3_best = X_history[best_idx]
            return x1_best, context.static_inputs['x2'], x3_best

        # Verifica se atingiu máximo de iterações
        if len(y_history) >= self.max_iterations:
            print(f"⚠️  Máximo de {self.max_iterations} iterações atingido")
            if y_history:
                best_idx = np.argmax(y_history)
                x1_best, x3_best = X_history[best_idx]
                print(f"   Melhor resultado: output3 = {y_history[best_idx]:.2f}%")
                return x1_best, context.static_inputs['x2'], x3_best
            else:
                raise RuntimeError("Máximo de iterações atingido sem nenhum resultado")

        # Se não tem histórico suficiente, retorna pontos iniciais
        if len(X_history) < len(self.initial_points):
            print(f"📍 Retornando ponto inicial {self.initial_point_index + 1}/{len(self.initial_points)}")
            return self._get_next_initial_point()

        # Executa otimização Bayesiana
        print(f"🔍 Otimizando com {len(X_history)} pontos históricos...")
        x1_next, x3_next = self._optimize_with_bayesian(X_history, y_history)
        x2 = context.static_inputs['x2']

        print(f"   Sugestão: x1={x1_next:.3f}, x3={x3_next:.3f}")

        return x1_next, x2, x3_next

    def get_optimization_status(self) -> dict:
        """
        Retorna status atual da otimização.

        Returns:
            Dicionário com informações do status
        """
        if not context.is_configured():
            return {'error': 'Contexto não configurado'}

        X_history, y_history = self._get_history()

        status = {
            'cluster': context.cluster,
            'projeto': context.nome_projeto,
            'total_analises': len(y_history),
            'max_iteracoes': self.max_iterations,
            'threshold': self.target_threshold,
            'threshold_atingido': self._check_target_reached(y_history),
        }

        if y_history:
            status['melhor_output3'] = max(y_history)
            best_idx = np.argmax(y_history)
            status['melhor_x1'] = X_history[best_idx][0]
            status['melhor_x3'] = X_history[best_idx][1]
            status['media_output3'] = np.mean(y_history)

        return status

    def reset_initial_points(self):
        """Reseta o contador de pontos iniciais."""
        self.initial_point_index = 0


# Exemplo de uso
if __name__ == "__main__":
    from context import context

    # Configura contexto
    context.set_project("MeuProjeto")
    context.set_cluster("Cluster_01")
    context.set_static_inputs(x2=0.95, x4=10.5, x5=0.002)

    # Cria otimizador
    optimizer = TargetOptimizer()

    # Pega novos targets
    x1, x2, x3 = optimizer.get_new_targets()
    print(f"\nTargets sugeridos:")
    print(f"  Input 1 (x1): {x1}")
    print(f"  Input 2 (x2): {x2}")
    print(f"  Input 3 (x3): {x3}")

    # Verifica status
    status = optimizer.get_optimization_status()
    print(f"\nStatus da otimização:")
    for key, value in status.items():
        print(f"  {key}: {value}")
