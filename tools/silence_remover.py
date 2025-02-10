import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QProgressBar,
    QFrame, QSpinBox, QMessageBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
import subprocess

class SilenceRemover(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_dir = None
        self.setup_ui()
        
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
        title = QLabel("Remover Silêncio")
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

        # Nível de silêncio (dB)
        silence_layout = QHBoxLayout()
        silence_label = QLabel("Nível de silêncio (dB):")
        silence_label.setStyleSheet("color: white;")
        silence_layout.addWidget(silence_label)

        self.silence_spin = QDoubleSpinBox()
        self.silence_spin.setRange(-90, 0)
        self.silence_spin.setValue(-30)
        self.silence_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        silence_layout.addWidget(self.silence_spin)
        config_layout.addLayout(silence_layout)

        # Duração mínima do silêncio
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duração mínima do silêncio (segundos):")
        duration_label.setStyleSheet("color: white;")
        duration_layout.addWidget(duration_label)

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 10)
        self.duration_spin.setValue(1.0)
        self.duration_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        duration_layout.addWidget(self.duration_spin)
        config_layout.addLayout(duration_layout)

        layout.addWidget(config_frame)

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
            
        # Verifica se o FFmpeg está disponível
        if not self.check_ffmpeg():
            QMessageBox.critical(self, "Erro", "FFmpeg não encontrado! Por favor, instale o FFmpeg primeiro.")
            return

        try:
            # Cria pasta para o vídeo processado
            output_folder = os.path.join(
                self.output_dir,
                f"sem_silencio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(output_folder, exist_ok=True)
            
            # Nome do arquivo de saída
            output_file = os.path.join(
                output_folder,
                f"video_sem_silencio.mp4"
            )
            
            # Configura a interface
            self.process_btn.setEnabled(False)
            self.select_video_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.status_label.setText("Processando vídeo...")
            self.status_label.setStyleSheet("color: #4a90e2;")
            
            # Executa o FFmpeg para detectar e remover silêncio
            silence_level = self.silence_spin.value()
            min_duration = self.duration_spin.value()
            
            subprocess.run([
                'ffmpeg',
                '-i', self.input_file,
                '-af', f'silenceremove=stop_periods=-1:stop_duration={min_duration}:stop_threshold={silence_level}dB',
                '-c:v', 'copy',
                output_file
            ], check=True)
            
            # Finaliza
            self.process_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
            self.status_label.setText("Processamento concluído!")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress_bar.hide()
            
            QMessageBox.information(
                self,
                "Sucesso",
                f"Processamento concluído!\nO vídeo foi salvo em:\n{output_file}"
            )
            
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar vídeo: {str(e)}")
            self.process_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}")
            self.process_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
