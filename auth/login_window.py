from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .auth_manager import AuthManager

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("WebDark Studio")
        self.setFixedSize(280, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container principal com padding
        main_container = QWidget()
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(25, 35, 25, 35)
        
        # Estilo geral
        self.setStyleSheet("""
            QMainWindow, QWidget#mainContainer {
                background-color: #0f0f15;
            }
            QLineEdit {
                padding: 10px;
                background-color: #1a1b26;
                color: #c0caf5;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                selection-background-color: #7aa2f7;
            }
            QLineEdit:focus {
                background-color: #24283b;
            }
            QLineEdit::placeholder {
                color: #565f89;
            }
            QPushButton {
                padding: 10px;
                font-size: 13px;
                font-weight: 500;
                border-radius: 6px;
                min-height: 38px;
            }
            QPushButton#primary {
                background-color: #7aa2f7;
                color: white;
                border: none;
            }
            QPushButton#primary:hover {
                background-color: #6b91e6;
            }
            QPushButton#primary:pressed {
                background-color: #5c80d5;
            }
            QPushButton#secondary {
                background-color: #1a1b26;
                border: none;
                color: #7aa2f7;
            }
            QPushButton#secondary:hover {
                background-color: #24283b;
            }
            QPushButton#secondary:pressed {
                background-color: #2c3047;
            }
            QLabel#title {
                color: #c0caf5;
            }
            QLabel#subtitle {
                color: #565f89;
            }
        """)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo/Título
        title = QLabel("WebDark")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        # Subtítulo
        self.subtitle = QLabel("Entre com seu email")
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(13)
        self.subtitle.setFont(subtitle_font)
        header_layout.addWidget(self.subtitle)
        
        main_layout.addWidget(header)
        
        # Formulário
        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Campo de email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(42)
        form_layout.addWidget(self.email_input)
        
        # Container para campos de senha
        self.password_container = QWidget()
        self.password_container.hide()
        password_layout = QVBoxLayout(self.password_container)
        password_layout.setSpacing(16)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        # Campo de senha
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setFixedHeight(42)
        password_layout.addWidget(self.password_input)
        
        # Campo de confirmação de senha
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirme sua senha")
        self.confirm_password_input.setFixedHeight(42)
        self.confirm_password_input.hide()
        password_layout.addWidget(self.confirm_password_input)
        
        form_layout.addWidget(self.password_container)
        main_layout.addWidget(form)
        
        # Botões
        buttons = QWidget()
        buttons_layout = QVBoxLayout(buttons)
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.continue_btn = QPushButton("Continuar")
        self.continue_btn.setObjectName("primary")
        self.continue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_btn.clicked.connect(self.check_email)
        buttons_layout.addWidget(self.continue_btn)
        
        self.back_btn = QPushButton("Voltar")
        self.back_btn.setObjectName("secondary")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.handle_back)
        self.back_btn.hide()
        buttons_layout.addWidget(self.back_btn)
        
        main_layout.addWidget(buttons)
        
        # Adiciona o container principal ao layout
        layout.addWidget(main_container)
    
    def check_email(self):
        """Verifica se o email existe e mostra os campos apropriados"""
        email = self.email_input.text().strip()
        
        if not email:
            QMessageBox.warning(self, "Erro", "Por favor, digite seu email.")
            return
        
        print(f"\nVerificando email: {email}")
        # Verifica se email existe
        check = self.auth_manager.check_email(email)
        print(f"Resultado da verificação: {check}")
        
        if check["exists"]:
            print("Email existe, mostrando tela de login")
            # Email existe, mostra apenas campo de senha
            self.show_login_fields()
        else:
            print("Email não existe, mostrando tela de cadastro")
            # Email não existe, mostra campos para cadastro
            self.show_signup_fields()
    
    def show_login_fields(self):
        """Mostra campos para login"""
        self.subtitle.setText("Digite sua senha")
        self.email_input.setEnabled(False)
        
        # Limpa os campos primeiro
        self.password_input.clear()
        self.confirm_password_input.clear()
        
        # Mostra container de senha
        self.password_container.show()
        
        # Mostra campo de senha
        self.password_input.show()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setFocus()
        
        # Esconde campo de confirmação
        self.confirm_password_input.hide()
        
        self.continue_btn.setText("Entrar")
        self.continue_btn.clicked.disconnect()
        self.continue_btn.clicked.connect(self.handle_login)
        
        self.back_btn.show()
    
    def show_signup_fields(self):
        """Mostra campos para cadastro"""
        print("Mostrando campos de cadastro")
        self.subtitle.setText("Crie sua senha")
        self.email_input.setEnabled(False)
        
        # Limpa os campos primeiro
        self.password_input.clear()
        self.confirm_password_input.clear()
        
        # Mostra container de senha
        self.password_container.show()
        
        # Mostra campos de senha
        self.password_input.show()
        self.password_input.setPlaceholderText("Senha")
        
        # Mostra campo de confirmação
        self.confirm_password_input.show()
        self.confirm_password_input.setPlaceholderText("Confirme sua senha")
        
        self.password_input.setFocus()
        
        self.continue_btn.setText("Criar Conta")
        self.continue_btn.clicked.disconnect()
        self.continue_btn.clicked.connect(self.handle_signup)
        
        self.back_btn.show()
    
    def handle_back(self):
        """Volta para a tela inicial"""
        self.subtitle.setText("Entre com seu email")
        self.email_input.setEnabled(True)
        self.email_input.clear()
        self.email_input.setFocus()
        
        # Esconde container de senha
        self.password_container.hide()
        
        # Limpa os campos
        self.password_input.clear()
        self.confirm_password_input.clear()
        
        # Reseta o botão continuar
        self.continue_btn.setText("Continuar")
        self.continue_btn.clicked.disconnect()
        self.continue_btn.clicked.connect(self.check_email)
        
        self.back_btn.hide()
        self.continue_btn.clicked.disconnect()
        self.continue_btn.clicked.connect(self.check_email)
        
        self.back_btn.hide()
    
    def handle_login(self):
        """Faz login com email e senha"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Erro", "Por favor, digite sua senha.")
            return
        
        # Tenta fazer login
        result = self.auth_manager.sign_in(email, password)
        
        if result["success"]:
            # Verifica status do usuário
            status = self.auth_manager.get_user_status(email)
            if status == "active":
                self.login_successful.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Erro", "Sua conta está inativa. Entre em contato com o suporte.")
        else:
            QMessageBox.warning(self, "Erro", str(result["error"]))
    
    def sign_in(self):
        """Faz login com email e senha"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Erro", "Por favor, digite sua senha.")
            return
        
        # Tenta fazer login
        result = self.auth_manager.sign_in(email, password)
        
        if result["success"]:
            # Verifica status do usuário
            status = self.auth_manager.get_user_status(email)
            if status == "active":
                # Não mostra mensagem para login bem sucedido
                self.login_successful.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Erro", "Sua conta está inativa. Entre em contato com o suporte.")
        else:
            QMessageBox.warning(self, "Erro", str(result["error"]))
    
    def handle_signup(self):
        """Cria nova conta"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Erro", "Por favor, digite uma senha.")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return
        
        # Tenta criar conta
        result = self.auth_manager.sign_up(email, password)
        
        if result["success"]:
            if result.get("is_new_account", True):  # Verifica se é conta nova
                QMessageBox.information(self, "Sucesso", "Conta criada com sucesso!")
            # O sign_up já faz login automaticamente
            self.login_successful.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Erro", str(result["error"]))
