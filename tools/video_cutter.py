import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QProgressBar,
    QFrame, QSpinBox, QMessageBox, QCheckBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
import subprocess

class VideoCutter(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_dir = None
        self.setup_ui()

class VideoCutter(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_dir = None
        self.processor = None
        
        # Verifica se o FFmpeg está instalado
        if not self.check_ffmpeg():
            QMessageBox.critical(
                self,
                "Erro",
                "FFmpeg não encontrado! Por favor, instale o FFmpeg usando:\n\n" +
                "1. Instale o Homebrew:\n" +
                "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\n\n" +
                "2. Instale o FFmpeg:\n" +
                "brew install ffmpeg"
            )
        
        self.setup_ui()
    
    def check_ffmpeg(self) -> bool:
        """Verifica se o FFmpeg está instalado."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
            
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Título
        title = QLabel("Cortar Vídeos")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Frame para seleção de arquivo
        file_frame = QFrame()
        file_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        file_layout = QVBoxLayout(file_frame)

        # Botão para selecionar vídeo
        self.select_video_btn = QPushButton("Selecionar Vídeo")
        self.select_video_btn.setStyleSheet("""
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
        self.select_video_btn.clicked.connect(self.select_video)
        file_layout.addWidget(self.select_video_btn)
        
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
        file_layout.addWidget(self.select_output_btn)

        # Label para mostrar o arquivo selecionado
        self.file_label = QLabel("Nenhum arquivo selecionado")
        self.file_label.setStyleSheet("color: white;")
        file_layout.addWidget(self.file_label)

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

        # Duração dos segmentos
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duração dos segmentos (segundos):")
        duration_label.setStyleSheet("color: white;")
        duration_layout.addWidget(duration_label)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(3, 60)
        self.duration_spin.setValue(10)
        self.duration_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        duration_layout.addWidget(self.duration_spin)
        config_layout.addLayout(duration_layout)

        # Checkbox para fade
        self.fade_check = QCheckBox("Adicionar fade out entre os cortes")
        self.fade_check.setChecked(True)
        self.fade_check.setStyleSheet("color: white;")
        config_layout.addWidget(self.fade_check)

        layout.addWidget(config_frame)

        # Lista de segmentos processados
        self.segments_list = QListWidget()
        self.segments_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.segments_list)

        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("Processar Vídeo")
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

    def select_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Vídeo",
            "",
            "Arquivos de Vídeo (*.mp4 *.avi *.mkv *.mov);;Todos os arquivos (*.*)"
        )
        
        if file_name:
            self.input_file = file_name
            self.file_label.setText(f"Arquivo: {os.path.basename(file_name)}")
            self.process_btn.setEnabled(True)
            
            # Se ainda não tiver pasta de destino, usa a pasta do vídeo
            if not self.output_dir:
                self.output_dir = os.path.dirname(file_name)
    
    def select_output_dir(self):
        """Abre diálogo para selecionar pasta de destino."""
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Destino",
            self.output_dir if self.output_dir else ""
        )
        
        if dir_name:
            self.output_dir = dir_name
            self.file_label.setText(f"Pasta de destino: {dir_name}")

    def start_processing(self):
        if not self.input_file:
            return
            
        # Verifica novamente se o FFmpeg está disponível
        if not self.check_ffmpeg():
            self.show_error("FFmpeg não encontrado! Por favor, instale o FFmpeg primeiro.")
            return

        try:
            # Obtém informações do vídeo usando ffprobe
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', self.input_file],
                capture_output=True,
                text=True
            )
            duration = float(result.stdout.strip())
            
            # Calcula os segmentos
            segment_duration = self.duration_spin.value()
            # Configura a interface
            self.process_btn.setEnabled(False)
            self.select_video_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            
            # Prepara os parâmetros
            segment_duration = self.duration_spin.value()
            current_time = 0
            segment_number = 1
            
            # Cria pasta para os cortes
            output_folder = os.path.join(
                self.output_dir,
                f"cortes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(output_folder, exist_ok=True)
            
            # Processa cada segmento
            while current_time < duration:
                # Nome do arquivo de saída
                output_file = os.path.join(
                    output_folder,
                    f"segmento_{segment_number:03d}.mp4"
                )
                
                # Atualiza a interface
                self.status_label.setText(f"Processando segmento {segment_number}...")
                self.status_label.setStyleSheet("color: #4a90e2;")
                
                # Executa o FFmpeg para cortar o vídeo
                subprocess.run([
                    'ffmpeg',
                    '-i', self.input_file,
                    '-ss', str(current_time),
                    '-t', str(segment_duration),
                    '-c', 'copy',
                    output_file
                ], check=True)
                
                # Atualiza o progresso
                progress = int((current_time / duration) * 100)
                self.progress_bar.setValue(progress)
                
                current_time += segment_duration
                segment_number += 1
            
            # Finaliza
            self.process_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
            self.status_label.setText("Processamento concluído!")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress_bar.hide()
            
            QMessageBox.information(
                self,
                "Sucesso",
                f"Processamento concluído!\nOs segmentos foram salvos em:\n{output_folder}"
            )

        except Exception as e:
            self.show_error(f"Erro ao iniciar processamento: {str(e)}")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #4a90e2;")

    def show_error(self, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #e74c3c;")
        QMessageBox.critical(self, "Erro", message)
        self.process_btn.setEnabled(True)
        self.select_video_btn.setEnabled(True)

    def add_segment_to_list(self, filename):
        item = QListWidgetItem(os.path.basename(filename))
        item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaPlay))
        self.segments_list.addItem(item)
        self.segments_list.scrollToBottom()

    def processing_finished(self):
        self.process_btn.setEnabled(True)
        self.select_video_btn.setEnabled(True)
        self.status_label.setText("Processamento concluído!")
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        self.progress_bar.hide()
        
        QMessageBox.information(
            self,
            "Sucesso",
            f"Processamento concluído!\nOs segmentos foram salvos em:\n{self.output_dir}"
        )
