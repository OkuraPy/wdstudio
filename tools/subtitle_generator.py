import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QProgressBar,
    QFrame, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
import subprocess
import speech_recognition as sr
from pydub import AudioSegment
import json

class SubtitleGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.output_dir = None
        self.recognizer = sr.Recognizer()
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
        title = QLabel("Gerar Legendas")
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

        # Seleção de idioma
        language_layout = QHBoxLayout()
        language_label = QLabel("Idioma:")
        language_label.setStyleSheet("color: white;")
        language_layout.addWidget(language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Português", "English", "Español"])
        self.language_combo.setStyleSheet("""
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
        language_layout.addWidget(self.language_combo)
        config_layout.addLayout(language_layout)

        # Formato de saída
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        format_label.setStyleSheet("color: white;")
        format_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["SRT", "VTT"])
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

        layout.addWidget(config_frame)

        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("Gerar Legendas")
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
            # Cria pasta para as legendas
            output_folder = os.path.join(
                self.output_dir,
                f"legendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            os.makedirs(output_folder, exist_ok=True)
            
            # Configura a interface
            self.process_btn.setEnabled(False)
            self.select_video_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.status_label.setText("Extraindo áudio...")
            self.status_label.setStyleSheet("color: #4a90e2;")
            
            # Extrai o áudio do vídeo
            audio_file = os.path.join(output_folder, "audio.wav")
            subprocess.run([
                'ffmpeg',
                '-i', self.input_file,
                '-vn',  # Sem vídeo
                '-acodec', 'pcm_s16le',  # Formato WAV
                '-ar', '16000',  # Sample rate
                '-ac', '1',  # Mono
                audio_file
            ], check=True)
            
            # Carrega o áudio
            audio = AudioSegment.from_wav(audio_file)
            
            # Configura o idioma
            language_map = {
                "Português": "pt-BR",
                "English": "en-US",
                "Español": "es-ES"
            }
            language = language_map[self.language_combo.currentText()]
            
            # Processa o áudio em chunks de 30 segundos
            chunk_length = 30 * 1000  # 30 segundos em milissegundos
            chunks = len(audio) // chunk_length
            subtitles = []
            
            for i, chunk_start in enumerate(range(0, len(audio), chunk_length)):
                # Atualiza progresso
                progress = int((i / chunks) * 100)
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"Processando áudio... {progress}%")
                
                # Extrai chunk
                chunk = audio[chunk_start:chunk_start + chunk_length]
                chunk_file = os.path.join(output_folder, f"chunk_{i}.wav")
                chunk.export(chunk_file, format="wav")
                
                # Reconhece fala
                with sr.AudioFile(chunk_file) as source:
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data, language=language)
                        if text:
                            start_time = chunk_start / 1000  # Converte para segundos
                            end_time = (chunk_start + len(chunk)) / 1000
                            subtitles.append({
                                'start': start_time,
                                'end': end_time,
                                'text': text
                            })
                    except sr.UnknownValueError:
                        pass  # Silêncio ou fala não reconhecida
                    except sr.RequestError as e:
                        QMessageBox.warning(
                            self,
                            "Aviso",
                            f"Erro ao acessar o serviço de reconhecimento: {str(e)}"
                        )
                
                # Remove arquivo temporário
                os.remove(chunk_file)
            
            # Remove arquivo de áudio
            os.remove(audio_file)
            
            # Salva legendas no formato escolhido
            format = self.format_combo.currentText()
            output_file = os.path.join(
                output_folder,
                f"legendas.{format.lower()}"
            )
            
            if format == "SRT":
                self._save_srt(subtitles, output_file)
            else:  # VTT
                self._save_vtt(subtitles, output_file)
            
            # Finaliza
            self.process_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
            self.status_label.setText("Processamento concluído!")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress_bar.hide()
            
            QMessageBox.information(
                self,
                "Sucesso",
                f"Processamento concluído!\nAs legendas foram salvas em:\n{output_file}"
            )
            
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar vídeo: {str(e)}")
            self.process_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}")
            self.process_btn.setEnabled(True)
            self.select_video_btn.setEnabled(True)
            
    def _format_time(self, seconds):
        """Formata tempo em segundos para o formato HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")
    
    def _save_srt(self, subtitles, output_file):
        """Salva legendas no formato SRT"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, subtitle in enumerate(subtitles, 1):
                f.write(f"{i}\n")
                f.write(f"{self._format_time(subtitle['start'])} --> {self._format_time(subtitle['end'])}\n")
                f.write(f"{subtitle['text']}\n\n")
    
    def _save_vtt(self, subtitles, output_file):
        """Salva legendas no formato VTT"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for subtitle in subtitles:
                start = self._format_time(subtitle['start']).replace(",", ".")
                end = self._format_time(subtitle['end']).replace(",", ".")
                f.write(f"{start} --> {end}\n")
                f.write(f"{subtitle['text']}\n\n")
