import sys
from PyQt6.QtWidgets import QApplication
from auth.login_window import LoginWindow

def main():
    print("Iniciando WebDark Studio...")
    app = QApplication(sys.argv)
    
    # Cria e configura a janela de login
    window = LoginWindow()
    window.setWindowTitle("WebDark Studio - Login")
    
    # Conecta o sinal de login bem sucedido
    def on_login_success():
        print("Login realizado com sucesso!")
        print("Iniciando WebDark Studio...")
        # Aqui você pode adicionar o código para abrir a janela principal
    
    window.login_successful.connect(on_login_success)
    
    # Exibe a janela
    window.show()
    
    # Inicia o loop de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
