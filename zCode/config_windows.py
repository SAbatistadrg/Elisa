from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator
import sys


class ConfigWindow:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.window = QWidget()
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Variáveis para armazenar os valores
        self.i1 = None
        self.i2 = None
        self.i3 = None
        self.i4 = None
        self.i5 = None
        self.i6 = None
        self.started = False
        self.cancelled = False
        
        # Estilo escuro
        self.window.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 1px solid #1a1a1a;
            }
            QLabel#header {
                background-color: #1e1e1e;
                color: #e0e0e0;
                padding: 20px;
                font-weight: 600;
                border-bottom: 2px solid #404040;
            }
            QLabel {
                color: #c0c0c0;
                font-size: 10pt;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #606060;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 12px 24px;
                font-weight: 500;
                min-width: 100px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QPushButton#startBtn {
                background-color: #27ae60;
            }
            QPushButton#startBtn:hover {
                background-color: #229954;
            }
            QPushButton#cancelBtn {
                background-color: #c0392b;
            }
            QPushButton#cancelBtn:hover {
                background-color: #a93226;
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Cabeçalho
        header = QLabel("ANP", self.window)
        header.setObjectName("header")
        header.setFont(QFont("Segoe UI", 14))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Container do conteúdo
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #2b2b2b; border: none;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(20)
        
        # Título
        title = QLabel("Configurações de Processamento")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #e0e0e0; padding-bottom: 10px;")
        content_layout.addWidget(title)
        
        # Formulário de inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Validador para floats
        float_validator = QDoubleValidator()
        float_validator.setNotation(QDoubleValidator.StandardNotation)
        
        # Input 1
        self.input1 = QLineEdit("0.001")
        self.input1.setValidator(float_validator)
        label1 = QLabel("Base Subamostra Não Refinado:")
        label1.setToolTip("Padrão: 0.001m")
        form_layout.addRow(label1, self.input1)
        
        # Input 2
        self.input2 = QLineEdit("0.5")
        self.input2.setValidator(float_validator)
        label2 = QLabel("Base Confiabilidade:")
        label2.setToolTip("Padrão: 0.5m")
        form_layout.addRow(label2, self.input2)
        
        # Input 3
        self.input3 = QLineEdit("0.001")
        self.input3.setValidator(float_validator)
        label3 = QLabel("Base Subamostra Refinado:")
        label3.setToolTip("Padrão: 0.001m")
        form_layout.addRow(label3, self.input3)
        
        # Input 4
        self.input4 = QLineEdit("10")
        self.input4.setValidator(float_validator)
        label4 = QLabel("Distância Máxima de Pesquisa:")
        label4.setToolTip("Padrão: 10m")
        form_layout.addRow(label4, self.input4)
        
        # Input 5
        self.input5 = QLineEdit("30")
        self.input5.setValidator(float_validator)
        label5 = QLabel("Número Máximo de Iterações:")
        label5.setToolTip("Padrão: 30")
        form_layout.addRow(label5, self.input5)
        
        # Input 6
        self.input6 = QLineEdit("95")
        self.input6.setValidator(float_validator)
        label6 = QLabel("Critério de Parada (%):")
        label6.setToolTip("Padrão: 95%")
        form_layout.addRow(label6, self.input6)
        
        content_layout.addLayout(form_layout)
        content_layout.addStretch()
        
        # Footer com botões
        footer_widget = QWidget()
        footer_widget.setStyleSheet("background-color: #1e1e1e; border: none; border-top: 1px solid #404040;")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(40, 20, 40, 20)
        footer_layout.setSpacing(15)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFont(QFont("Segoe UI", 10))
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._on_cancel)
        
        self.start_btn = QPushButton("Iniciar")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFont(QFont("Segoe UI", 10))
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._on_start)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.cancel_btn)
        footer_layout.addWidget(self.start_btn)
        
        main_layout.addWidget(content_widget)
        main_layout.addWidget(footer_widget)
        
        self.window.setLayout(main_layout)
        
        # Centralizar na tela
        screen = self.app.primaryScreen().geometry()
        width, height = 600, 520
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        
        self.window.setGeometry(x, y, width, height)
        self.window.show()
    
    def _on_cancel(self):
        """Cancela e fecha o programa"""
        self.cancelled = True
        self.window.close()
        sys.exit(0)
    
    def _on_start(self):
        """Captura os valores e fecha a janela"""
        try:
            self.i1 = float(self.input1.text())
            self.i2 = float(self.input2.text())
            self.i3 = float(self.input3.text())
            self.i4 = float(self.input4.text())
            self.i5 = float(self.input5.text())
            self.i6 = float(self.input6.text())
            
            self.started = True
            self.window.close()
        except ValueError:
            # Se algum valor estiver inválido, não fecha
            pass
    
    def wait_for_start(self):
        """Aguarda o usuário clicar em Iniciar"""
        self.app.exec_()
        return self.started
    
    def get_values(self):
        """Retorna os valores configurados"""
        return {
            'i1': self.i1,
            'i2': self.i2,
            'i3': self.i3,
            'i4': self.i4,
            'i5': self.i5,
            'i6': self.i6
        }


# Exemplo de uso:
if __name__ == "__main__":
    config = ConfigWindow()
    
    # Aguarda o usuário clicar em Iniciar
    if config.wait_for_start():
        values = config.get_values()
        print("Valores configurados:")
        print(f"i1: {values['i1']}")
        print(f"i2: {values['i2']}")
        print(f"i3: {values['i3']}")
        print(f"i4: {values['i4']}")
        print(f"i5: {values['i5']}")
        print(f"i6: {values['i6']}")
    else:
        print("Cancelado pelo usuário")