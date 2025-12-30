from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
from context import context
import sys
import math

class SpinnerWidget(QWidget):
    """Widget de spinner animado personalizado"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.setFixedSize(40, 40)
        
        # Timer para animar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(30)  # Atualiza a cada 30ms para suavidade
    
    def rotate(self):
        self.angle = (self.angle + 15) % 360
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Centro do widget
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 4
        
        # Desenhar círculo de loading
        for i in range(12):
            angle = math.radians(self.angle + i * 30)
            x1 = center_x + radius * 0.6 * math.cos(angle)
            y1 = center_y + radius * 0.6 * math.sin(angle)
            x2 = center_x + radius * math.cos(angle)
            y2 = center_y + radius * math.sin(angle)
            
            # Opacidade gradual
            opacity = 255 - (i * 20)
            color = QColor(160, 160, 160, max(opacity, 30))
            pen = QPen(color, 3, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))


class StatusWindow:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.window = QWidget()
        self.window.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        
        # Estilo escuro/cinza
        self.window.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 1px solid #1a1a1a;
            }
            QLabel#header {
                background-color: #1e1e1e;
                color: #e0e0e0;
                padding: 15px;
                font-weight: 600;
                border-bottom: 2px solid #404040;
            }
            QLabel#status {
                color: #c0c0c0;
                padding: 10px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QPushButton#pauseBtn {
                background-color: #505050;
            }
            QPushButton#pauseBtn:hover {
                background-color: #5a5a5a;
            }
            QPushButton#cancelBtn {
                background-color: #c0392b;
            }
            QPushButton#cancelBtn:hover {
                background-color: #a93226;
            }
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #1e1e1e;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #606060;
                border-radius: 3px;
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Cabeçalho
        self.header = QLabel("ANP", self.window)
        self.header.setObjectName("header")
        self.header.setFont(QFont("Segoe UI", 11))
        self.header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.header)
        
        # Container do conteúdo
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #2b2b2b; border: none;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 25, 25, 20)
        content_layout.setSpacing(15)
        
        # Spinner de loading
        spinner_container = QHBoxLayout()
        spinner_container.setAlignment(Qt.AlignCenter)
        
        self.spinner = SpinnerWidget(self.window)
        spinner_container.addWidget(self.spinner)
        content_layout.addLayout(spinner_container)
        
        content_layout.addSpacing(5)
        
        # Cluster atual
        self.cluster_label = QLabel(f"Cluster atual: {context.cluster}", self.window)
        self.cluster_label.setFont(QFont("Segoe UI", 9))
        self.cluster_label.setAlignment(Qt.AlignCenter)
        self.cluster_label.setStyleSheet("color: #909090; padding: 5px;")
        content_layout.addWidget(self.cluster_label)
        
        # Status
        self.status_label = QLabel("Iniciando...", self.window)
        self.status_label.setObjectName("status")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(50)
        content_layout.addWidget(self.status_label)
        
        # Espaçamento
        content_layout.addSpacing(10)
        
        # Botões
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.pause_btn = QPushButton("Pausar", self.window)
        self.pause_btn.setObjectName("pauseBtn")
        self.pause_btn.setFont(QFont("Segoe UI", 9))
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        
        self.cancel_btn = QPushButton("Cancelar", self.window)
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFont(QFont("Segoe UI", 9))
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._on_cancel)
        
        button_layout.addStretch()
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.cancel_btn)
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_widget)
        self.window.setLayout(main_layout)
        
        # Posicionamento e tamanho
        screen = self.app.primaryScreen().geometry()
        width, height = 400, 220
        x = screen.width() - width - 20
        y = screen.height() - height - 60
        
        self.window.setGeometry(x, y, width, height)
        self.window.show()
        
        # Timer para processar eventos e manter animação
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_ui)
        self.timer.start(30)
    
    def _update_ui(self):
        """Mantém a UI responsiva e força atualização do spinner"""
        self.app.processEvents()
        if hasattr(self, 'spinner'):
            self.spinner.update()
    
    def _on_cancel(self):
        """Cancela a execução e encerra o programa"""
        self.close()
        sys.exit(0)
    
    def update(self, message):
        """Atualiza a mensagem de status e o cluster"""
        self.status_label.setText(message)
        self.cluster_label.setText(f"Cluster atual: {context.cluster}")
        self.app.processEvents()
    
    def set_program_name(self, name):
        """Define o nome do programa no cabeçalho"""
        self.header.setText(name)
        self.app.processEvents()
    
    def close(self):
        """Fecha a janela"""
        self.window.close()
        self.timer.stop()


# Exemplo de uso:
if __name__ == "__main__":
    status = StatusWindow()
    status.update("Processando dados...")
    
    # Conectar botões (exemplo)
    status.pause_btn.clicked.connect(lambda: print("Pausado!"))
    # O botão cancelar já está conectado internamente para matar o programa
    
    sys.exit(status.app.exec_())