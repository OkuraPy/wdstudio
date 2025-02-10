import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, 
    QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
    QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtGui import QIcon, QFont, QScreen
from PyQt6.QtCore import Qt, QSize
from auth_web.login_web import show_auth_window

class ToolButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        self.setFixedSize(QSize(200, 50))
        self.setFont(QFont('Arial', 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
            }
            QPushButton:pressed {
                background-color: #4a90e2;
            }
        """)

class WebDarkStudio(QMainWindow):
    def __init__(self):
        print("\nInicializando WebDark Studio...")
        super().__init__()
        self.setWindowTitle("WebDark Studio")
        self.setMinimumSize(1200, 800)
        print("Configurando interface...")
        self.setup_ui()
        print("Interface configurada com sucesso")

    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Barra lateral (menu)
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #1e1e1e;")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        # Logo/Título
        title = QLabel("WebDark Studio")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)

        # Separador após o título
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #3b3b3b;")
        sidebar_layout.addWidget(separator)
        sidebar_layout.addSpacing(20)

        # Botões das ferramentas
        tools = [
            ("Ferramentas de Vídeo", [
                ("Baixar do Pexels", self.show_pexels_downloader),
                ("Cortar Vídeos", self.show_video_cutter)
            ]),
            ("Ferramentas de Áudio", [
                ("Remover Silêncio", self.show_silence_remover),
                ("Gerar Legendas", self.show_subtitle_generator)
            ]),
            ("Ferramentas de Imagem", [
                ("Converter Formato", self.show_image_converter),
                ("Gerenciar Arquivos", self.show_file_manager)
            ]),
            ("Ferramentas de Organização", [
                ("Criar Estrutura", self.show_folder_creator)
            ])
        ]

        for category, items in tools:
            # Título da categoria
            cat_label = QLabel(category)
            cat_label.setStyleSheet("color: #4a90e2; font-size: 14px; font-weight: bold;")
            sidebar_layout.addWidget(cat_label)
            
            # Botões da categoria
            for name, callback in items:
                btn = ToolButton(name)
                btn.clicked.connect(callback)
                sidebar_layout.addWidget(btn)
            
            sidebar_layout.addSpacing(20)

        # Área de conteúdo principal
        content_area = QFrame()
        content_area.setStyleSheet("background-color: #2b2b2b;")
        
        # StackedWidget para alternar entre as ferramentas
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #2b2b2b;")
        
        # Layout para a área de conteúdo
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.stacked_widget)

        # Adiciona sidebar e área de conteúdo ao layout principal
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)

        # Página inicial
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_label = QLabel("Bem-vindo ao WebDark Studio!")
        welcome_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        
        desc_label = QLabel("Selecione uma ferramenta no menu lateral para começar.")
        desc_label.setStyleSheet("color: #cccccc; font-size: 18px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(desc_label)
        
        self.stacked_widget.addWidget(welcome_widget)

    # Métodos para mostrar cada ferramenta
    def show_pexels_downloader(self):
        from tools.pexels_downloader import PexelsDownloader
        # Remove o widget atual se existir
        current_widget = self.stacked_widget.currentWidget()
        if current_widget:
            self.stacked_widget.removeWidget(current_widget)
        
        # Cria e adiciona o novo widget
        pexels_widget = PexelsDownloader()
        self.stacked_widget.addWidget(pexels_widget)
        self.stacked_widget.setCurrentWidget(pexels_widget)

    def show_video_cutter(self):
        try:
            from tools.video_cutter import VideoCutter
            # Remove o widget atual se existir
            current_widget = self.stacked_widget.currentWidget()
            if current_widget:
                self.stacked_widget.removeWidget(current_widget)
            
            # Cria e adiciona o novo widget
            video_cutter = VideoCutter()
            self.stacked_widget.addWidget(video_cutter)
            self.stacked_widget.setCurrentWidget(video_cutter)
        except Exception as e:
            import traceback
            print(f"Erro ao carregar Video Cutter: {str(e)}")
            print("Detalhes do erro:")
            traceback.print_exc()

    def show_silence_remover(self):
        try:
            from tools.silence_remover import SilenceRemover
            # Remove o widget atual se existir
            current_widget = self.stacked_widget.currentWidget()
            if current_widget:
                self.stacked_widget.removeWidget(current_widget)
            
            # Cria e adiciona o novo widget
            silence_remover = SilenceRemover()
            self.stacked_widget.addWidget(silence_remover)
            self.stacked_widget.setCurrentWidget(silence_remover)
        except Exception as e:
            import traceback
            print(f"Erro ao carregar Silence Remover: {str(e)}")
            print("Detalhes do erro:")
            traceback.print_exc()

    def show_subtitle_generator(self):
        try:
            from tools.subtitle_generator import SubtitleGenerator
            # Remove o widget atual se existir
            current_widget = self.stacked_widget.currentWidget()
            if current_widget:
                self.stacked_widget.removeWidget(current_widget)
            
            # Cria e adiciona o novo widget
            subtitle_generator = SubtitleGenerator()
            self.stacked_widget.addWidget(subtitle_generator)
            self.stacked_widget.setCurrentWidget(subtitle_generator)
        except Exception as e:
            import traceback
            print(f"Erro ao carregar Subtitle Generator: {str(e)}")
            print("Detalhes do erro:")
            traceback.print_exc()

    def show_image_converter(self):
        try:
            from tools.image_converter import ImageConverter
            # Remove o widget atual se existir
            current_widget = self.stacked_widget.currentWidget()
            if current_widget:
                self.stacked_widget.removeWidget(current_widget)
            
            # Cria e adiciona o novo widget
            image_converter = ImageConverter()
            self.stacked_widget.addWidget(image_converter)
            self.stacked_widget.setCurrentWidget(image_converter)
        except Exception as e:
            import traceback
            print(f"Erro ao carregar Image Converter: {str(e)}")
            print("Detalhes do erro:")
            traceback.print_exc()

    def show_file_manager(self):
        try:
            from tools.file_manager import FileManager
            # Remove o widget atual se existir
            current_widget = self.stacked_widget.currentWidget()
            if current_widget:
                self.stacked_widget.removeWidget(current_widget)
            
            # Cria e adiciona o novo widget
            file_manager = FileManager()
            self.stacked_widget.addWidget(file_manager)
            self.stacked_widget.setCurrentWidget(file_manager)
        except Exception as e:
            import traceback
            print(f"Erro ao carregar File Manager: {str(e)}")
            print("Detalhes do erro:")
            traceback.print_exc()

    def show_folder_creator(self):
        try:
            from tools.folder_creator import FolderCreator
            # Remove o widget atual se existir
            current_widget = self.stacked_widget.currentWidget()
            if current_widget:
                self.stacked_widget.removeWidget(current_widget)
            
            # Cria e adiciona o novo widget
            folder_creator = FolderCreator()
            self.stacked_widget.addWidget(folder_creator)
            self.stacked_widget.setCurrentWidget(folder_creator)
        except Exception as e:
            import traceback
            print(f"Erro ao carregar Folder Creator: {str(e)}")
            print("Detalhes do erro:")
            traceback.print_exc()

# Variável global para manter referência à janela principal
main_window = None

def show_main_window():
    print("Abrindo janela principal...")
    try:
        # Mostra a tela de login web primeiro
        if show_auth_window():  # Se o login foi bem sucedido
            global main_window
            main_window = WebDarkStudio()
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
            print("Janela principal aberta com sucesso")
            return True
        else:
            print("Login não realizado")
            return False
    except Exception as e:
        print(f"Erro ao abrir janela principal: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Iniciando aplicação...")
    try:
        # Garantir que só existe uma instância do QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        app.setStyle('Fusion')  # Estilo moderno e consistente
        
        # Mostrar a janela principal (que vai mostrar o login web primeiro)
        if not show_main_window():  # Se o login não foi bem sucedido
            print("Encerrando aplicação...")
            return 0
        
        print("Aplicação iniciada com sucesso")
        return app.exec()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()
