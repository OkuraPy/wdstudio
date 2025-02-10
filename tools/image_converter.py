import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QProgressBar,
    QFrame, QComboBox, QMessageBox, QSpinBox,
    QCheckBox, QListWidget
)
from PyQt6.QtCore import Qt
from PIL import Image

class ImageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.input_files = []
        self.output_dir = None
        self.setup_ui()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Título
        title = QLabel("Converter Imagens")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Frame para seleção de arquivos
        file_frame = QFrame()
        file_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        file_layout = QVBoxLayout(file_frame)

        # Botões de seleção
        buttons_layout = QHBoxLayout()
        
        # Botão para selecionar imagens
        self.select_images_btn = QPushButton("Selecionar Imagens")
        self.select_images_btn.setStyleSheet("""
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
        """)
        self.select_images_btn.clicked.connect(self.select_images)
        buttons_layout.addWidget(self.select_images_btn)
        
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
        buttons_layout.addWidget(self.select_output_btn)
        
        file_layout.addLayout(buttons_layout)

        # Lista de arquivos selecionados
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #3d3d3d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
            }
        """)
        file_layout.addWidget(self.file_list)

        layout.addWidget(file_frame)

        # Frame para configurações
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        config_layout = QVBoxLayout(config_frame)

        # Formato de saída
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        format_label.setStyleSheet("color: white;")
        format_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG", "WEBP", "GIF"])
        self.format_combo.setStyleSheet("""
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
        format_layout.addWidget(self.format_combo)
        config_layout.addLayout(format_layout)

        # Qualidade (para JPEG e WEBP)
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Qualidade:")
        quality_label.setStyleSheet("color: white;")
        quality_layout.addWidget(quality_label)

        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(85)
        self.quality_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        quality_layout.addWidget(self.quality_spin)
        config_layout.addLayout(quality_layout)

        # Opções adicionais
        self.resize_check = QCheckBox("Redimensionar")
        self.resize_check.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #3d3d3d;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
            }
        """)
        self.resize_check.stateChanged.connect(self.toggle_resize_options)
        config_layout.addWidget(self.resize_check)

        # Opções de redimensionamento (inicialmente ocultas)
        self.resize_options = QFrame()
        resize_layout = QVBoxLayout(self.resize_options)
        
        # Largura
        width_layout = QHBoxLayout()
        width_label = QLabel("Largura:")
        width_label.setStyleSheet("color: white;")
        width_layout.addWidget(width_label)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(1920)
        self.width_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        width_layout.addWidget(self.width_spin)
        resize_layout.addLayout(width_layout)
        
        # Altura
        height_layout = QHBoxLayout()
        height_label = QLabel("Altura:")
        height_label.setStyleSheet("color: white;")
        height_layout.addWidget(height_label)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(1080)
        self.height_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        height_layout.addWidget(self.height_spin)
        resize_layout.addLayout(height_layout)
        
        # Manter proporção
        self.keep_aspect = QCheckBox("Manter proporção")
        self.keep_aspect.setChecked(True)
        self.keep_aspect.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #3d3d3d;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a90e2;
            }
        """)
        resize_layout.addWidget(self.keep_aspect)
        
        self.resize_options.hide()
        config_layout.addWidget(self.resize_options)

        layout.addWidget(config_frame)

        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("Converter")
        self.process_btn.setEnabled(False)
        self.process_btn.setStyleSheet("""
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
        self.process_btn.clicked.connect(self.start_processing)
        actions_layout.addWidget(self.process_btn)

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
        
    def toggle_resize_options(self, state):
        """Mostra/oculta opções de redimensionamento."""
        self.resize_options.setVisible(state == Qt.CheckState.Checked.value)

    def select_images(self):
        """Abre diálogo para selecionar imagens."""
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Imagens",
            "",
            "Imagens (*.png *.jpg *.jpeg *.gif *.webp);;Todos os arquivos (*.*)"
        )
        
        if file_names:
            self.input_files = file_names
            self.file_list.clear()
            for file in file_names:
                self.file_list.addItem(os.path.basename(file))
            self.process_btn.setEnabled(True)
            
            # Se ainda não tiver pasta de destino, usa a pasta da primeira imagem
            if not self.output_dir:
                self.output_dir = os.path.dirname(file_names[0])
    
    def select_output_dir(self):
        """Abre diálogo para selecionar pasta de destino."""
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Destino",
            self.output_dir if self.output_dir else ""
        )
        
        if dir_name:
            self.output_dir = dir_name

    def start_processing(self):
        if not self.input_files:
            return

        try:
            # Cria pasta para as imagens convertidas
            output_folder = os.path.join(
                self.output_dir,
                f"convertidas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(output_folder, exist_ok=True)
            
            # Configura a interface
            self.process_btn.setEnabled(False)
            self.select_images_btn.setEnabled(False)
            self.progress_bar.setMaximum(len(self.input_files))
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            
            # Configurações
            format = self.format_combo.currentText().lower()
            quality = self.quality_spin.value()
            resize = self.resize_check.isChecked()
            width = self.width_spin.value() if resize else None
            height = self.height_spin.value() if resize else None
            keep_aspect = self.keep_aspect.isChecked()
            
            # Processa cada imagem
            for i, input_file in enumerate(self.input_files):
                self.status_label.setText(f"Processando {os.path.basename(input_file)}...")
                self.progress_bar.setValue(i + 1)
                
                # Abre a imagem
                with Image.open(input_file) as img:
                    # Converte para RGB se necessário (alguns formatos não suportam RGBA)
                    if format == "jpeg" and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # Redimensiona se necessário
                    if resize:
                        if keep_aspect:
                            # Calcula nova altura mantendo proporção
                            ratio = min(width/img.width, height/img.height)
                            new_width = int(img.width * ratio)
                            new_height = int(img.height * ratio)
                        else:
                            new_width = width
                            new_height = height
                        
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Nome do arquivo de saída
                    output_file = os.path.join(
                        output_folder,
                        f"{os.path.splitext(os.path.basename(input_file))[0]}.{format}"
                    )
                    
                    # Salva a imagem
                    if format in ("jpeg", "webp"):
                        img.save(output_file, quality=quality, optimize=True)
                    else:
                        img.save(output_file, optimize=True)
            
            # Finaliza
            self.process_btn.setEnabled(True)
            self.select_images_btn.setEnabled(True)
            self.status_label.setText("Processamento concluído!")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress_bar.hide()
            
            QMessageBox.information(
                self,
                "Sucesso",
                f"Processamento concluído!\nAs imagens foram salvas em:\n{output_folder}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}")
            self.process_btn.setEnabled(True)
            self.select_images_btn.setEnabled(True)
