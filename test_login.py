import sys
from PyQt6.QtWidgets import QApplication
from auth.login_window import LoginWindow

def main():
    print("Iniciando aplicação...")
    app = QApplication(sys.argv)
    print("QApplication criada")
    
    window = LoginWindow()
    print("Janela de login criada")
    
    window.show()
    print("Janela exibida")
    
    print("Iniciando loop de eventos...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
