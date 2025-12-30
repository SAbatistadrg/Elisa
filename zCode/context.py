# context.py
import pygetwindow as gw

class AnalysisContext:
    def __init__(self):
        self.nome_projeto = None
        self.cluster = None
        self.criterio = 90
        self.static_inputs = {
            'x2': None,  # confiabilidade
            'x4': None,  # dmp
            'x5': None   # nmi
        }
        self.dinamic_inputs = {
            'x1': None,  # subamostraNR
            'x3': None,  # subamostraR
        }

    def set_project_from_window(self):
        """Extrai o nome do projeto do título da janela ativa"""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                window_title = active_window.title
                # Extrai tudo antes de " - SCENE"
                if " - SCENE" in window_title:
                    self.nome_projeto = window_title.split(" - SCENE")[0].strip()
                    return True
                else:
                    print("Aviso: Título da janela não contém ' - SCENE'")
                    return False
            else:
                print("Erro: Nenhuma janela ativa encontrada")
                return False
        except Exception as e:
            print(f"Erro ao capturar título da janela: {e}")
            return False

    def set_project(self, nome_projeto):
        """Define o projeto manualmente (fallback)"""
        self.nome_projeto = nome_projeto

    def set_cluster(self, cluster):
        """Define o cluster atual"""
        self.cluster = cluster

    def set_criterio(self, criterio):
        """Define o cluster atual"""
        self.criterio = criterio

    def set_static_inputs(self, x2, x4, x5):
        """Define os inputs estáticos (2, 4, 5)"""
        self.static_inputs['x2'] = x2
        self.static_inputs['x4'] = x4
        self.static_inputs['x5'] = x5

    def set_minimum_dinamic_inputs(self, x1, x3):
        """Define os inputs estáticos (2, 4, 5)"""
        self.dinamic_inputs['x1'] = x1
        self.dinamic_inputs['x3'] = x3

    def is_configured(self):
        """Verifica se o contexto está completo"""
        return (self.nome_projeto is not None 
                and self.cluster is not None 
                and all(v is not None for v in self.static_inputs.values()))

    def reset(self):
        """Reseta o contexto"""
        self.nome_projeto = None
        self.cluster = None
        self.static_inputs = {
            'x2': None,
            'x4': None,
            'x5': None
        }

# Instância global única
context = AnalysisContext()
