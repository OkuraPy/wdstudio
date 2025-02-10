import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QProgressBar,
    QFrame, QTextEdit, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

class FolderCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.output_dir = None
        self.setup_ui()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Título
        title = QLabel("Criar Estrutura de Pastas")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Frame para seleção de pasta
        dir_frame = QFrame()
        dir_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        dir_layout = QVBoxLayout(dir_frame)
        
        # Botão para selecionar pasta de destino
        self.select_output_btn = QPushButton("Selecionar Pasta de Destino")
        self.select_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.select_output_btn.clicked.connect(self.select_output_dir)
        dir_layout.addWidget(self.select_output_btn)

        # Label para mostrar o diretório selecionado
        self.output_label = QLabel("Pasta de destino: Nenhuma selecionada")
        self.output_label.setStyleSheet("color: white;")
        dir_layout.addWidget(self.output_label)

        layout.addWidget(dir_frame)

        # Frame para templates
        template_frame = QFrame()
        template_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        template_layout = QVBoxLayout(template_frame)

        # Templates pré-definidos
        template_layout.addWidget(QLabel("Templates:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Personalizado",
            "Projeto de Vídeo",
            "Projeto de Foto",
            "Projeto de Desenvolvimento",
            "Projeto de Documentos"
        ])
        self.template_combo.setStyleSheet("""
            QComboBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.template_combo.currentIndexChanged.connect(self.load_template)
        template_layout.addWidget(self.template_combo)

        layout.addWidget(template_frame)

        # Frame para estrutura
        structure_frame = QFrame()
        structure_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        structure_layout = QVBoxLayout(structure_frame)

        # Explicação do formato
        help_text = """Formato:
- Uma pasta por linha
- Use / para criar subpastas
- Use # para comentários
- Linhas em branco são ignoradas

Exemplo:
videos/
    brutos/
    editados/
    thumbnails/
assets/
    musicas/
    efeitos/
"""
        help_label = QLabel(help_text)
        help_label.setStyleSheet("color: #cccccc;")
        structure_layout.addWidget(help_label)

        # Editor de texto para a estrutura
        self.structure_edit = QTextEdit()
        self.structure_edit.setStyleSheet("""
            QTextEdit {
                background-color: #3d3d3d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                font-family: monospace;
            }
        """)
        structure_layout.addWidget(self.structure_edit)

        layout.addWidget(structure_frame)

        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("Criar Estrutura")
        self.create_btn.setEnabled(False)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        self.create_btn.clicked.connect(self.create_structure)
        actions_layout.addWidget(self.create_btn)

        layout.addLayout(actions_layout)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4a90e2;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #cccccc;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()
        
        # Carrega template inicial
        self.load_template(0)
    
    def select_output_dir(self):
        """Abre diálogo para selecionar pasta de destino."""
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Destino",
            self.output_dir if self.output_dir else ""
        )
        
        if dir_name:
            self.output_dir = dir_name
            self.output_label.setText(f"Pasta de destino: {dir_name}")
            self.create_btn.setEnabled(True)

    def load_template(self, index):
        """Carrega template selecionado."""
        templates = {
            "Projeto de Vídeo": """# Estrutura para projetos de vídeo
videos/
    brutos/           # Arquivos originais
    editados/         # Vídeos editados
    thumbnails/       # Miniaturas
assets/
    musicas/         # Músicas de fundo
    efeitos/         # Efeitos sonoros
    graficos/        # Elementos visuais
    fontes/          # Fontes personalizadas
projetos/            # Arquivos do editor
referencias/         # Vídeos de referência
documentos/          # Roteiros e anotações""",

            "Projeto de Foto": """# Estrutura para projetos de foto
originais/           # Fotos originais
editadas/           # Fotos editadas
    web/            # Versões para web
    impressao/      # Versões para impressão
assets/
    presets/        # Presets do Lightroom/Photoshop
    texturas/       # Texturas e overlays
backup/             # Backup das fotos originais
referencias/        # Imagens de referência""",

            "Projeto de Desenvolvimento": """# Estrutura para projetos de desenvolvimento
src/                # Código fonte
    components/     # Componentes reutilizáveis
    utils/          # Funções utilitárias
    assets/         # Recursos estáticos
docs/               # Documentação
    api/            # Documentação da API
    guias/          # Guias de uso
tests/              # Testes automatizados
build/              # Arquivos compilados
config/             # Arquivos de configuração
scripts/            # Scripts de automação""",

            "Projeto de Documentos": """# Estrutura para projetos de documentos
documentos/
    contratos/      # Contratos e acordos
    financeiro/     # Documentos financeiros
    relatorios/     # Relatórios e análises
templates/          # Modelos de documentos
referencias/        # Material de referência
arquivados/         # Documentos antigos
backup/             # Backup dos documentos""",

            "Personalizado": """# Estrutura personalizada
pasta1/
    subpasta1/
    subpasta2/
pasta2/
    subpasta3/
    subpasta4/"""
        }
        
        template_name = self.template_combo.currentText()
        if template_name in templates:
            self.structure_edit.setText(templates[template_name])

    def create_structure(self):
        """Cria a estrutura de pastas."""
        if not self.output_dir:
            return

        try:
            # Configura a interface
            self.create_btn.setEnabled(False)
            self.select_output_btn.setEnabled(False)
            self.progress_bar.show()
            self.status_label.setText("Criando estrutura...")
            
            # Processa o texto
            lines = [
                line.strip() for line in self.structure_edit.toPlainText().split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
            
            # Configura a barra de progresso
            self.progress_bar.setMaximum(len(lines))
            self.progress_bar.setValue(0)
            
            # Cria as pastas
            created = []
            for i, line in enumerate(lines):
                # Remove espaços extras e barras
                path = line.strip().strip("/")
                if path:
                    # Cria o caminho completo
                    full_path = os.path.join(self.output_dir, path)
                    os.makedirs(full_path, exist_ok=True)
                    created.append(path)
                
                # Atualiza progresso
                self.progress_bar.setValue(i + 1)
            
            # Finaliza
            self.create_btn.setEnabled(True)
            self.select_output_btn.setEnabled(True)
            self.status_label.setText("Estrutura criada!")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress_bar.hide()
            
            # Mostra resumo
            message = "Estrutura criada com sucesso!\n\nPastas criadas:\n"
            message += "\n".join(f"- {path}" for path in created)
            
            QMessageBox.information(
                self,
                "Sucesso",
                message
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar estrutura: {str(e)}")
            self.create_btn.setEnabled(True)
            self.select_output_btn.setEnabled(True)
