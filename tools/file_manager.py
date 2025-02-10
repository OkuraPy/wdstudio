import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QProgressBar,
    QFrame, QListWidget, QMessageBox, QLineEdit,
    QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt

class FileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.input_dir = None
        self.output_dir = None
        self.setup_ui()
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Título
        title = QLabel("Gerenciar Arquivos")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Frame para seleção de diretórios
        dir_frame = QFrame()
        dir_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        dir_layout = QVBoxLayout(dir_frame)

        # Botões de seleção
        buttons_layout = QHBoxLayout()
        
        # Botão para selecionar pasta de entrada
        self.select_input_btn = QPushButton("Selecionar Pasta de Entrada")
        self.select_input_btn.setStyleSheet("""
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
        self.select_input_btn.clicked.connect(self.select_input_dir)
        buttons_layout.addWidget(self.select_input_btn)
        
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
        
        dir_layout.addLayout(buttons_layout)

        # Labels para mostrar os diretórios selecionados
        self.input_label = QLabel("Pasta de entrada: Nenhuma selecionada")
        self.input_label.setStyleSheet("color: white;")
        dir_layout.addWidget(self.input_label)
        
        self.output_label = QLabel("Pasta de destino: Nenhuma selecionada")
        self.output_label.setStyleSheet("color: white;")
        dir_layout.addWidget(self.output_label)

        layout.addWidget(dir_frame)

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

        # Filtros de arquivo
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtrar por extensão (ex: jpg,png):")
        filter_label.setStyleSheet("color: white;")
        filter_layout.addWidget(filter_label)

        self.filter_edit = QLineEdit()
        self.filter_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        filter_layout.addWidget(self.filter_edit)
        config_layout.addLayout(filter_layout)

        # Opções de organização
        self.organize_by_date = QCheckBox("Organizar por data")
        self.organize_by_date.setStyleSheet("""
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
        config_layout.addWidget(self.organize_by_date)

        self.organize_by_type = QCheckBox("Organizar por tipo")
        self.organize_by_type.setStyleSheet("""
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
        config_layout.addWidget(self.organize_by_type)

        # Opções de limpeza
        self.remove_duplicates = QCheckBox("Remover duplicados")
        self.remove_duplicates.setStyleSheet("""
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
        config_layout.addWidget(self.remove_duplicates)

        # Tamanho mínimo
        size_layout = QHBoxLayout()
        size_label = QLabel("Tamanho mínimo (KB):")
        size_label.setStyleSheet("color: white;")
        size_layout.addWidget(size_label)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(0, 1000000)
        self.size_spin.setValue(0)
        self.size_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        size_layout.addWidget(self.size_spin)
        config_layout.addLayout(size_layout)

        layout.addWidget(config_frame)

        # Lista de arquivos encontrados
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
        layout.addWidget(self.file_list)

        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("Escanear")
        self.scan_btn.setEnabled(False)
        self.scan_btn.setStyleSheet("""
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
        self.scan_btn.clicked.connect(self.scan_files)
        actions_layout.addWidget(self.scan_btn)
        
        self.process_btn = QPushButton("Processar")
        self.process_btn.setEnabled(False)
        self.process_btn.setStyleSheet("""
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

    def select_input_dir(self):
        """Abre diálogo para selecionar pasta de entrada."""
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Entrada",
            self.input_dir if self.input_dir else ""
        )
        
        if dir_name:
            self.input_dir = dir_name
            self.input_label.setText(f"Pasta de entrada: {dir_name}")
            self.scan_btn.setEnabled(True)
    
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

    def scan_files(self):
        """Escaneia arquivos na pasta de entrada."""
        if not self.input_dir:
            return

        try:
            self.file_list.clear()
            self.status_label.setText("Escaneando arquivos...")
            self.scan_btn.setEnabled(False)
            
            # Obtém filtros
            extensions = [ext.strip().lower() for ext in self.filter_edit.text().split(",") if ext.strip()]
            min_size = self.size_spin.value() * 1024  # Converte para bytes
            
            # Lista todos os arquivos
            files = []
            for root, _, filenames in os.walk(self.input_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    # Verifica extensão
                    if extensions:
                        ext = os.path.splitext(filename)[1][1:].lower()
                        if ext not in extensions:
                            continue
                    
                    # Verifica tamanho
                    if min_size > 0:
                        size = os.path.getsize(file_path)
                        if size < min_size:
                            continue
                    
                    files.append(file_path)
            
            # Mostra arquivos encontrados
            for file in files:
                self.file_list.addItem(os.path.relpath(file, self.input_dir))
            
            # Atualiza interface
            self.scan_btn.setEnabled(True)
            self.process_btn.setEnabled(len(files) > 0)
            self.status_label.setText(f"Encontrados {len(files)} arquivos")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao escanear arquivos: {str(e)}")
            self.scan_btn.setEnabled(True)

    def start_processing(self):
        """Processa os arquivos conforme as configurações."""
        if not self.input_dir:
            return
            
        # Se não tiver pasta de destino, usa a pasta de entrada
        if not self.output_dir:
            self.output_dir = self.input_dir

        try:
            # Configura a interface
            self.process_btn.setEnabled(False)
            self.scan_btn.setEnabled(False)
            self.progress_bar.setMaximum(self.file_list.count())
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            
            # Cria pasta para os arquivos processados
            output_base = os.path.join(
                self.output_dir,
                f"organizados_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(output_base, exist_ok=True)
            
            # Lista de arquivos já copiados (para evitar duplicados)
            copied_files = set()
            
            # Processa cada arquivo
            for i in range(self.file_list.count()):
                rel_path = self.file_list.item(i).text()
                input_path = os.path.join(self.input_dir, rel_path)
                
                self.status_label.setText(f"Processando {rel_path}...")
                self.progress_bar.setValue(i + 1)
                
                # Verifica se é duplicado
                if self.remove_duplicates:
                    file_hash = self._get_file_hash(input_path)
                    if file_hash in copied_files:
                        continue
                    copied_files.add(file_hash)
                
                # Determina pasta de destino
                if self.organize_by_date:
                    # Organiza por ano/mês
                    timestamp = os.path.getmtime(input_path)
                    date = datetime.fromtimestamp(timestamp)
                    rel_dir = os.path.join(
                        str(date.year),
                        f"{date.month:02d}"
                    )
                elif self.organize_by_type:
                    # Organiza por extensão
                    ext = os.path.splitext(rel_path)[1][1:].lower()
                    rel_dir = ext if ext else "sem_extensao"
                else:
                    # Mantém estrutura original
                    rel_dir = os.path.dirname(rel_path)
                
                # Cria pasta de destino
                output_dir = os.path.join(output_base, rel_dir)
                os.makedirs(output_dir, exist_ok=True)
                
                # Copia arquivo
                output_path = os.path.join(output_dir, os.path.basename(rel_path))
                shutil.copy2(input_path, output_path)
            
            # Finaliza
            self.process_btn.setEnabled(True)
            self.scan_btn.setEnabled(True)
            self.status_label.setText("Processamento concluído!")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress_bar.hide()
            
            QMessageBox.information(
                self,
                "Sucesso",
                f"Processamento concluído!\nOs arquivos foram salvos em:\n{output_base}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar arquivos: {str(e)}")
            self.process_btn.setEnabled(True)
            self.scan_btn.setEnabled(True)
    
    def _get_file_hash(self, file_path, chunk_size=8192):
        """Calcula hash do arquivo para detectar duplicados."""
        import hashlib
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                hasher.update(chunk)
                chunk = f.read(chunk_size)
        return hasher.hexdigest()
