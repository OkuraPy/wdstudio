import sys, os
import textwrap
import io
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QFileDialog,
    QVBoxLayout, QLabel, QProgressBar, QTextEdit, QComboBox, QLineEdit
)
from PyQt5.QtCore import QThread, pyqtSignal
from pydub import AudioSegment, silence
import speech_recognition as sr

# Configuração para localizar o ffmpeg.exe
if getattr(sys, 'frozen', False):
    # Quando o aplicativo estiver empacotado, usamos o diretório do executável
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

ffmpeg_path = os.path.join(base_path, "ffmpeg.exe")
if os.path.isfile(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path
else:
    # Caso não encontre o ffmpeg.exe na mesma pasta, tenta utilizar o comando 'ffmpeg' do PATH do sistema
    AudioSegment.converter = "ffmpeg"

def format_timestamp(ms):
    """
    Converte milissegundos em uma string de timestamp no formato SRT: HH:MM:SS,mmm
    """
    hours = int(ms / 3600000)
    minutes = int((ms % 3600000) / 60000)
    seconds = int((ms % 60000) / 1000)
    milliseconds = int(ms % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def split_text_into_chunks(text, max_line_length=35):
    """
    Divide o texto em blocos de uma única linha com no máximo max_line_length caracteres.
    Não corta palavras (exceto se uma palavra for maior que o limite).
    """
    chunks = textwrap.wrap(
        text,
        width=max_line_length,
        break_long_words=False,
        break_on_hyphens=False
    )
    return chunks

class SubtitleWorker(QThread):
    # Sinais para atualizar a interface
    progress = pyqtSignal(int)     # Emite o progresso em porcentagem
    log = pyqtSignal(str)          # Emite mensagens de log
    finished = pyqtSignal(str)     # Emite o caminho do arquivo SRT gerado (ou string vazia em caso de erro)

    def __init__(self, audio_file, language, parent=None):
        super().__init__(parent)
        self.audio_file = audio_file
        # Código do idioma para reconhecimento (ex: "pt-BR", "en-US", etc.)
        self.language = language
        # Define o caminho do arquivo SRT para ser salvo na mesma pasta do áudio, usando o mesmo nome base
        directory = os.path.dirname(self.audio_file)
        base_name = os.path.splitext(os.path.basename(self.audio_file))[0]
        self.srt_file = os.path.join(directory, f"{base_name}.srt")

    def run(self):
        # Carrega o arquivo de áudio
        try:
            audio = AudioSegment.from_file(self.audio_file)
            self.log.emit("Áudio carregado com sucesso.")
        except Exception as e:
            self.log.emit(f"Erro ao carregar o arquivo de áudio: {e}")
            self.finished.emit("")
            return

        # Detecta os intervalos de fala (não-silêncio)
        nonsilent_ranges = silence.detect_nonsilent(
            audio, min_silence_len=700, silence_thresh=-40)
        if not nonsilent_ranges:
            nonsilent_ranges = [[0, len(audio)]]
            self.log.emit("Nenhum silêncio detectado; o áudio será processado como um único segmento.")
        else:
            self.log.emit(f"Foram encontrados {len(nonsilent_ranges)} segmentos de fala.")

        recognizer = sr.Recognizer()
        subtitles = []
        total_segments = len(nonsilent_ranges)
        subtitle_counter = 1  # Contador para a numeração dos blocos SRT

        # Processa cada segmento de fala
        for seg_index, (start_ms, end_ms) in enumerate(nonsilent_ranges, start=1):
            segment = audio[start_ms:end_ms]

            # Exporta o segmento para um buffer em memória (BytesIO) para agilizar o processamento
            buffer = io.BytesIO()
            segment.export(buffer, format="wav")
            buffer.seek(0)

            # Realiza o reconhecimento de fala usando o áudio do buffer
            with sr.AudioFile(buffer) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language=self.language)
                except Exception as e:
                    text = "[Erro de reconhecimento ou áudio sem fala]"
                    self.log.emit(f"Segmento {seg_index}: {e}")

            # Divide o texto reconhecido em blocos de uma única linha com no máximo 35 caracteres
            chunks = split_text_into_chunks(text, max_line_length=35)

            # Se houver mais de um bloco, divide igualmente o tempo do segmento entre eles
            num_chunks = len(chunks)
            segment_duration = end_ms - start_ms
            for i, chunk in enumerate(chunks):
                chunk_start = start_ms + int(i * segment_duration / num_chunks)
                chunk_end = start_ms + int((i + 1) * segment_duration / num_chunks)
                start_timestamp = format_timestamp(chunk_start)
                end_timestamp = format_timestamp(chunk_end)
                subtitle_block = f"{subtitle_counter}\n{start_timestamp} --> {end_timestamp}\n{chunk}\n"
                subtitles.append(subtitle_block)
                subtitle_counter += 1

            # Atualiza o progresso (por segmento processado)
            progress_value = int((seg_index / total_segments) * 100)
            self.progress.emit(progress_value)

        # Salva as legendas no arquivo SRT
        try:
            with open(self.srt_file, "w", encoding="utf-8") as f:
                f.write("\n".join(subtitles))
            self.log.emit(f"Legendas salvas em: {self.srt_file}")
        except Exception as e:
            self.log.emit(f"Erro ao salvar o arquivo SRT: {e}")
            self.finished.emit("")
            return

        self.finished.emit(self.srt_file)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Legendas SRT")
        self.resize(600, 500)
        self.worker = None

        # Widget central e layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Seleção do arquivo de áudio
        self.label_file = QLabel("Selecione um arquivo de áudio:")
        layout.addWidget(self.label_file)
        self.btn_select = QPushButton("Selecionar Arquivo")
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)

        # Seletor de idioma do áudio
        self.language_label = QLabel("Selecione o idioma do áudio:")
        layout.addWidget(self.language_label)
        self.language_combo = QComboBox()
        idiomas = [
            "Português do Brasil", "English", "Espanhol", "Francês", "Italiano",
            "Romeno", "Polonês", "Russo", "Japonês", "Coreano", "Canadense", "Outros"
        ]
        self.language_combo.addItems(idiomas)
        self.language_combo.currentIndexChanged.connect(self.update_language_input)
        layout.addWidget(self.language_combo)

        # Campo para inserir manualmente o código do idioma (habilitado somente se "Outros" for selecionado)
        self.language_input = QLineEdit()
        self.language_input.setPlaceholderText("Digite o código do idioma (ex: en-GB)")
        self.language_input.setEnabled(False)
        layout.addWidget(self.language_input)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Rodapé com crédito
        self.footer_label = QLabel("Sistema feito por WEBDARK")
        self.footer_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(self.footer_label)

        # Área de log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def update_language_input(self, index):
        """Habilita o campo de entrada se 'Outros' estiver selecionado."""
        if self.language_combo.currentText() == "Outros":
            self.language_input.setEnabled(True)
        else:
            self.language_input.setEnabled(False)

    def select_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo de Áudio", "",
            "Audio Files (*.wav *.mp3 *.ogg *.flac)", options=options
        )
        if file_name:
            self.log_text.append(f"Arquivo selecionado: {file_name}")
            self.start_processing(file_name)

    def start_processing(self, audio_file):
        self.progress_bar.setValue(0)
        mapping = {
            "Português do Brasil": "pt-BR",
            "English": "en-US",
            "Espanhol": "es-ES",
            "Francês": "fr-FR",
            "Italiano": "it-IT",
            "Romeno": "ro-RO",
            "Polonês": "pl-PL",
            "Russo": "ru-RU",
            "Japonês": "ja-JP",
            "Coreano": "ko-KR",
            "Canadense": "en-CA",
            "Outros": None
        }
        selected = self.language_combo.currentText()
        if selected == "Outros":
            lang_code = self.language_input.text().strip()
            if not lang_code:
                self.log_text.append("Por favor, insira o código do idioma no campo 'Outros'.")
                return
        else:
            lang_code = mapping.get(selected, "pt-BR")
        self.log_text.append(f"Idioma selecionado: {selected} ({lang_code})")
        self.worker = SubtitleWorker(audio_file, lang_code)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def append_log(self, message):
        self.log_text.append(message)

    def processing_finished(self, srt_file):
        if srt_file:
            self.append_log("Processamento concluído com sucesso!")
        else:
            self.append_log("Ocorreu um erro durante o processamento.")
        self.worker = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
