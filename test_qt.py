import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Teste PyQt")
    window.setGeometry(100, 100, 200, 100)
    
    button = QPushButton("Clique Aqui", window)
    button.move(50, 20)
    
    window.show()
    sys.exit(app.exec())
