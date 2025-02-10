import sys
import os
import random
import time
import datetime
import ffmpeg

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QLabel, QFileDialog, QProgressBar,
    QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


# ==================================================
# Função auxiliar para “embaralhar” os vídeos em uma pasta,
# com tratamento de PermissionError (WinError 32).
# ==================================================
def shuffle_folder(folder):
    video_files = [f for f in os.listdir(folder) if f.lower().endswith('.mp4')]
    if not video_files:
        print("Nenhum vídeo encontrado para embaralhar!")
        return

    random.shuffle(video_files)

    # Renomeia para nomes temporários (temp_*.mp4)
    for i, file in enumerate(video_files):
        old_path = os.path.join(folder, file)
        temp_path = os.path.join(folder, f"temp_{i:06d}.mp4")

        for attempt in range(3):
            try:
                os.rename(old_path, temp_path)
                break
            except PermissionError as e:
                if attempt < 2:
                    time.sleep(1)
                else:
                    raise e

    # Agora renomeia de temp_* para a ordem final
    temp_files = sorted(
        [f for f in os.listdir(folder) if f.startswith('temp_')])
    for i, file in enumerate(temp_files):
        old_path = os.path.join(folder, file)
        new_path = os.path.join(folder, f"{i+1:06d}.mp4")

        for attempt in range(3):
            try:
                os.rename(old_path, new_path)
                break
            except PermissionError as e:
                if attempt < 2:
                    time.sleep(1)
                else:
                    raise e

    print("Vídeos embaralhados com sucesso!")


# ==================================================
# Thread para renderização (concat + fade) usando NVENC
# e exibindo progresso + estimativa de tempo (ETA).
# ==================================================
class RenderThread(QThread):
    # Emite (progresso_em_% , tempo_restante_em_segundos)
    progress = pyqtSignal(int, float)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, video_files, output_file):
        super().__init__()
        self.video_files = video_files
        self.output_file = output_file
        self.is_running = True
        self.start_time = None

    def stop(self):
        self.is_running = False

    def run(self):
        try:
            total_files = len(self.video_files)
            concat_list = []

            # Armazenamos o tempo inicial para calcular ETA
            self.start_time = time.time()

            # Reencodar cada vídeo com fade (exceto no último),
            # mas reencodando o último para manter o mesmo formato (NVENC).
            for i, video_file in enumerate(self.video_files):
                if not self.is_running:
                    return

                fade_video = f"temp_fade_{i}.mp4"

                probe = ffmpeg.probe(video_file)
                duration = float(probe['format']['duration'])

                if i < total_files - 1:
                    # Aplica fade out de 1s (no final)
                    stream = ffmpeg.input(video_file)
                    stream = ffmpeg.filter(stream, 'fade',
                                           type='out',
                                           start_time=duration - 1,
                                           duration=1)
                    # Usa NVENC para acelerar
                    stream = ffmpeg.output(
                        stream,
                        fade_video,
                        vcodec='h264_nvenc',
                        preset='fast',
                        b='5M',
                        acodec='aac'
                    )
                    ffmpeg.run(stream,
                               overwrite_output=True,
                               capture_stdout=True,
                               capture_stderr=True)
                else:
                    # Último vídeo (sem fade) mas reencodado em NVENC
                    stream = ffmpeg.input(video_file)
                    stream = ffmpeg.output(
                        stream,
                        fade_video,
                        vcodec='h264_nvenc',
                        preset='fast',
                        b='5M',
                        acodec='aac'
                    )
                    ffmpeg.run(stream,
                               overwrite_output=True,
                               capture_stdout=True,
                               capture_stderr=True)

                concat_list.append(fade_video)

                # Calcula progresso (até ~50%) ao finalizar cada reencode
                step_progress = int(((i + 1) * 50) / total_files)
                time_elapsed = time.time() - self.start_time
                if step_progress > 0:
                    time_remaining = (
                        time_elapsed / step_progress) * (100 - step_progress)
                else:
                    time_remaining = 0
                self.progress.emit(step_progress, time_remaining)

            # Cria arquivo de lista para concat
            with open('concat_list.txt', 'w', encoding='utf-8') as f:
                for video in concat_list:
                    f.write(f"file '{video}'\n")

            # Concatenar todos (agora com copy)
            stream = ffmpeg.input('concat_list.txt', format='concat', safe=0)
            stream = ffmpeg.output(
                stream, self.output_file, acodec='copy', vcodec='copy')
            ffmpeg.run(stream,
                       overwrite_output=True,
                       capture_stdout=True,
                       capture_stderr=True)

            # Depois da concat final, progresso = 100%
            final_progress = 100
            time_elapsed = time.time() - self.start_time
            time_remaining = 0  # Já finalizamos
            self.progress.emit(final_progress, time_remaining)

            # Limpar arquivos temporários
            for i in range(total_files):
                try:
                    os.remove(f"temp_fade_{i}.mp4")
                except:
                    pass
            try:
                os.remove('concat_list.txt')
            except:
                pass

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


# ==================================================
# Thread para cortar vídeos em segmentos aleatórios
# com "fast seeking" p/ acelerar ainda mais.
# ==================================================
class VideoProcessThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, input_file, output_dir):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        try:
            if not self.is_running:
                return

            # Pega a duração total do vídeo
            probe = ffmpeg.probe(self.input_file)
            duration = float(probe['format']['duration'])

            start_time = 0
            segment_index = 1

            # Enquanto não atingir o fim do vídeo
            while start_time < duration:
                if not self.is_running:
                    self.finished.emit()
                    return

                # Define duração aleatória entre 3 e 10s
                cut_duration = random.randint(3, 10)
                end_time = start_time + cut_duration

                if end_time > duration:
                    end_time = duration
                    cut_duration = end_time - start_time

                if cut_duration < 3:
                    break

                output_file = os.path.join(
                    self.output_dir, f"{segment_index:06d}.mp4")

                # Para acelerar o corte:
                # -ss antes de -i = fast seek
                # -t para limitar a duração
                # -c copy = sem reencode
                (
                    ffmpeg
                    .input(self.input_file, ss=start_time)  # fast seek
                    .output(output_file, t=cut_duration, c='copy', **{'avoid_negative_ts': '1'})
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )

                # Atualiza progresso
                progress = int((start_time / duration) * 100)
                self.progress.emit(progress)

                if not self.is_running:
                    self.finished.emit()
                    return

                start_time = end_time
                segment_index += 1

            self.progress.emit(100)
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


# ==================================================
# Interface Principal (PyQt)
# ==================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Cutter - by WEBDARK")
        self.setFixedSize(600, 400)
        self.input_file = None
        self.output_dir = None

        # Estilos da interface
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid #4a90e2;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
            }
        """)

        # Layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title = QLabel("Video Cutter")
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Autor
        author = QLabel("by WEBDARK")
        author.setFont(QFont('Arial', 12))
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author)

        # Botões
        self.select_btn = QPushButton("Selecionar Vídeo")
        self.select_btn.clicked.connect(self.select_video)
        layout.addWidget(self.select_btn)

        self.cut_btn = QPushButton("Cortar Vídeo")
        self.cut_btn.clicked.connect(self.cut_video)
        self.cut_btn.setEnabled(False)
        layout.addWidget(self.cut_btn)

        self.shuffle_btn = QPushButton("Embaralhar Vídeos")
        self.shuffle_btn.clicked.connect(self.shuffle_videos)
        layout.addWidget(self.shuffle_btn)

        self.rename_btn = QPushButton("Renomear Vídeos")
        self.rename_btn.clicked.connect(self.rename_videos)
        layout.addWidget(self.rename_btn)

        self.render_btn = QPushButton("Renderizar Vídeos")
        self.render_btn.clicked.connect(self.render_videos)
        layout.addWidget(self.render_btn)

        # Barra de progresso + botão parar
        progress_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.stop_btn = QPushButton("Parar")
        self.stop_btn.clicked.connect(self.stop_cutting)
        self.stop_btn.setVisible(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        progress_layout.addWidget(self.stop_btn)

        layout.addLayout(progress_layout)

        # Label de status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Para controle de lotes
        # List of lists (cada sublista é um lote de arquivos)
        self.chunks_list = []
        self.current_chunk_index = 0  # Qual lote está sendo renderizado agora
        self.chunk_size = 0           # Tamanho do lote (ex. 400)

    # ----------------------------------------------
    # 1) Selecionar Vídeo para Corte
    # ----------------------------------------------
    def select_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Vídeo",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )

        if file_name:
            self.input_file = file_name
            self.output_dir = os.path.dirname(file_name)
            self.cut_btn.setEnabled(True)
            self.status_label.setText(
                f"Vídeo selecionado: {os.path.basename(file_name)}")

    # ----------------------------------------------
    # 2) Cortar Vídeo em Segmentos (usando fast seeking)
    # ----------------------------------------------
    def cut_video(self):
        if not self.input_file:
            self.status_label.setText("Selecione um vídeo primeiro!")
            return

        # Cria subpasta para cortes
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        cut_folder = os.path.join(self.output_dir, f"{base_name}_cuts")
        os.makedirs(cut_folder, exist_ok=True)

        self.progress_bar.setVisible(True)
        self.stop_btn.setVisible(True)
        self.progress_bar.setValue(0)

        self.cut_btn.setEnabled(False)
        self.select_btn.setEnabled(False)

        self.thread = VideoProcessThread(self.input_file, cut_folder)
        self.thread.progress.connect(self.update_cut_progress)
        self.thread.finished.connect(self.cutting_finished)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def update_cut_progress(self, value):
        self.progress_bar.setValue(value)

    def cutting_finished(self):
        self.status_label.setText("Cortes concluídos!")
        self.select_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.stop_btn.setVisible(False)

    def stop_cutting(self):
        if hasattr(self, 'thread'):
            self.thread.stop()
            self.status_label.setText("Processo interrompido pelo usuário!")
            self.select_btn.setEnabled(True)
            self.cut_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.stop_btn.setVisible(False)

    # ----------------------------------------------
    # 3) Embaralhar Vídeos em uma Pasta
    # ----------------------------------------------
    def shuffle_videos(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecione a Pasta com os Vídeos",
            ""
        )

        if not folder:
            return

        try:
            shuffle_folder(folder)
            self.status_label.setText("Vídeos embaralhados com sucesso!")
        except PermissionError as e:
            self.status_label.setText(
                f"Erro de permissão ao renomear: {str(e)}")

    # ----------------------------------------------
    # 4) Renomear Vídeos em uma Pasta (Sequencial)
    # ----------------------------------------------
    def rename_videos(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecione a Pasta com os Vídeos",
            ""
        )

        if not folder:
            return

        video_files = [f for f in os.listdir(
            folder) if f.lower().endswith('.mp4')]
        if not video_files:
            self.status_label.setText("Nenhum vídeo encontrado para renomear!")
            return

        start_number, ok = QInputDialog.getInt(
            self,
            "Renomear Vídeos",
            "Número inicial:",
            1,    # valor padrão
            1,    # mínimo
            1000000  # máximo
        )

        if ok:
            video_files.sort()

            for i, file in enumerate(video_files):
                old_path = os.path.join(folder, file)
                new_path = os.path.join(folder, f"{start_number + i:06d}.mp4")

                for attempt in range(3):
                    try:
                        os.rename(old_path, new_path)
                        break
                    except PermissionError as e:
                        if attempt < 2:
                            time.sleep(1)
                        else:
                            self.status_label.setText(
                                f"Erro ao renomear: {str(e)}")
                            return

            self.status_label.setText("Vídeos renomeados com sucesso!")

    # ----------------------------------------------
    # 5) Renderizar Vídeos (Concat + Fade via NVENC),
    #    agora em Lotes/Chunks
    # ----------------------------------------------
    def render_videos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Vídeos para Renderizar",
            "",
            "Video Files (*.mp4)"
        )

        if not files:
            return

        # Pergunta quantos arquivos por lote
        chunk_size, ok = QInputDialog.getInt(
            self,
            "Quantidade de arquivos por Lote",
            "Digite o número de arquivos por Lote:",
            400,   # valor padrão
            1,     # mínimo
            1000000  # máximo
        )
        if not ok:
            return

        # Ordena os arquivos (caso queira manter ordem)
        files.sort()

        # Divide em sublistas (chunks) de tamanho chunk_size
        self.chunks_list = []
        for i in range(0, len(files), chunk_size):
            chunk = files[i:i+chunk_size]
            self.chunks_list.append(chunk)

        # Reseta contadores
        self.current_chunk_index = 0
        self.chunk_size = chunk_size

        # Desabilita botões
        self.progress_bar.setVisible(True)
        self.stop_btn.setVisible(True)
        self.progress_bar.setValue(0)
        self.render_btn.setEnabled(False)
        self.select_btn.setEnabled(False)

        # Inicia renderização do primeiro lote
        self.status_label.setText("Iniciando renderização em lotes...")
        self.start_render_chunk()

    def start_render_chunk(self):
        """ Inicia a renderização do lote atual (self.current_chunk_index). """
        if self.current_chunk_index >= len(self.chunks_list):
            # Já renderizamos todos os lotes
            self.status_label.setText(
                "Renderização de todos os lotes concluída!")
            self.select_btn.setEnabled(True)
            self.render_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.stop_btn.setVisible(False)
            return

        # Pega o lote atual
        current_files = self.chunks_list[self.current_chunk_index]
        # Define nome de saída: render01, render02, etc.
        # Ex: se current_chunk_index=0 => render01; se=1 => render02...
        out_index = self.current_chunk_index + 1
        output_file = os.path.join(os.path.dirname(current_files[0]),
                                   f"render{out_index:02d}.mp4")

        # Inicia thread com esse lote
        self.render_thread = RenderThread(current_files, output_file)
        self.render_thread.progress.connect(self.update_render_progress)
        self.render_thread.finished.connect(self.chunk_finished)
        self.render_thread.error.connect(self.show_error)
        self.render_thread.start()

        # Mensagem de status
        total_lotes = len(self.chunks_list)
        self.status_label.setText(
            f"Renderizando lote {out_index}/{total_lotes}...")

    def chunk_finished(self):
        """ Chamado quando finaliza o render do lote atual. """
        self.current_chunk_index += 1
        self.start_render_chunk()  # Vai para o próximo lote

    # Recebe (value, eta) => progresso e tempo restante estimado
    def update_render_progress(self, value, eta):
        self.progress_bar.setValue(value)
        import datetime
        if eta < 0:
            eta = 0
        td = str(datetime.timedelta(seconds=int(eta)))

        total_lotes = len(self.chunks_list)
        out_index = self.current_chunk_index + 1
        self.status_label.setText(
            f"Renderizando lote {out_index}/{total_lotes}... "
            f"({value}% - ETA: {td})"
        )

    def stop_cutting(self):
        """ Botão 'Parar' tanto para corte como para render. """
        if hasattr(self, 'thread'):
            self.thread.stop()
        if hasattr(self, 'render_thread'):
            self.render_thread.stop()
        self.status_label.setText("Processo interrompido pelo usuário!")
        self.select_btn.setEnabled(True)
        self.cut_btn.setEnabled(True)
        self.render_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.stop_btn.setVisible(False)

    # ----------------------------------------------
    # Tratamento de erros
    # ----------------------------------------------
    def show_error(self, error_msg):
        self.status_label.setText(f"Erro: {error_msg}")
        self.select_btn.setEnabled(True)
        self.cut_btn.setEnabled(True)
        self.render_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.stop_btn.setVisible(False)


# ==================================================
# Execução da aplicação
# ==================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
