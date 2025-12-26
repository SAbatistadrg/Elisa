from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import sys

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
        
        self.window.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-radius: 10px;
                border: 2px solid #4CAF50;
            }
            QLabel {
                color: white;
                padding: 15px;
            }
        """)
        
        self.label = QLabel("Iniciando...", self.window)
        self.label.setFont(QFont("Arial", 11))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        
        screen = self.app.primaryScreen().geometry()
        width, height = 320, 100
        x = screen.width() - width - 20
        y = screen.height() - height - 60
        
        self.window.setGeometry(x, y, width, height)
        self.label.setGeometry(0, 0, width, height)
        
        self.window.show()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.app.processEvents)
        self.timer.start(50)
    
    def update(self, message):
        self.label.setText(message)
        self.app.processEvents()
    
    def close(self):
        self.window.close()
        self.timer.stop()