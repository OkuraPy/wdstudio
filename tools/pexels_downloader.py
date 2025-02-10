import os
import json
from typing import Optional, List, Dict
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QRadioButton, QButtonGroup,
    QPushButton, QProgressBar, QMessageBox,
    QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente (para API key)
load_dotenv()

@dataclass
class DownloadItem:
    url: str
    filename: str
    media_type: str  # 'image' ou 'video'
    width: int
    height: int

class DownloaderThread(QThread):
    status = pyqtSignal(str)  # Novo sinal para status detalhado
    progress = pyqtSignal(int, int)  # (current, total)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    item_completed = pyqtSignal(str)  # filename

    def __init__(self, items: List[DownloadItem], output_folder: str):
        super().__init__()
        self.items = items
        self.output_folder = output_folder
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        total = len(self.items)
        print(f"\nIniciando download de {total} itens...")
        for i, item in enumerate(self.items, 1):
            print(f"\nBaixando item {i}/{total}: {item.filename}")
            if not self.is_running:
                break

            try:
                self.status.emit(f"Conectando a {item.filename}...")
                response = requests.get(item.url, stream=True, timeout=(5, 30))
                response.raise_for_status()
                
                # Obtém o tamanho total do arquivo
                total_size = int(response.headers.get('content-length', 0))
                print(f"Tamanho do arquivo: {total_size/1024/1024:.2f} MB")
                
                self.status.emit(f"Baixando {item.filename}...")
                
                # Cria o nome do arquivo
                filename = os.path.join(self.output_folder, item.filename)
                
                # Download do arquivo em chunks
                downloaded_size = 0
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.is_running:
                            break
                        if chunk:
                            downloaded_size += len(chunk)
                            f.write(chunk)
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                self.status.emit(f"Baixando {item.filename}: {progress:.1f}%")
                
                self.item_completed.emit(filename)
                self.progress.emit(i, total)
                
            except Exception as e:
                self.error.emit(f"Erro ao baixar {item.filename}: {str(e)}")

        if self.is_running:
            self.finished.emit()

class PexelsDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('PEXELS_API_KEY', '')
        self.downloader = None
        self.setup_ui()

    def update_status(self, message: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #4a90e2;")
        QApplication.processEvents()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Título
        title = QLabel("Download de Mídia do Pexels")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Frame para API Key
        api_frame = QFrame()
        api_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        api_layout = QVBoxLayout(api_frame)
        
        api_label = QLabel("Chave API do Pexels:")
        api_label.setStyleSheet("color: white;")
        api_layout.addWidget(api_label)
        
        self.api_input = QLineEdit(self.api_key)
        self.api_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: none;
                border-radius: 4px;
            }
        """)
        api_layout.addWidget(self.api_input)
        
        save_api_btn = QPushButton("Salvar Chave API")
        save_api_btn.setStyleSheet("""
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
        save_api_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(save_api_btn)
        
        layout.addWidget(api_frame)

        # Frame para opções de busca
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        search_layout = QVBoxLayout(search_frame)

        # Campo de busca
        search_label = QLabel("Termo de busca:")
        search_label.setStyleSheet("color: white;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: none;
                border-radius: 4px;
            }
        """)
        search_layout.addWidget(self.search_input)

        # Tipo de mídia
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup(self)
        
        for text, value in [("Imagens", "photos"), ("Vídeos", "videos")]:
            radio = QRadioButton(text)
            radio.setStyleSheet("color: white;")
            radio.setProperty("value", value)
            self.type_group.addButton(radio)
            type_layout.addWidget(radio)
        
        self.type_group.buttons()[0].setChecked(True)
        search_layout.addLayout(type_layout)

        # Orientação
        orientation_layout = QHBoxLayout()
        self.orientation_group = QButtonGroup(self)
        
        for text, value in [("Qualquer", ""), ("Horizontal", "landscape"), ("Vertical", "portrait")]:
            radio = QRadioButton(text)
            radio.setStyleSheet("color: white;")
            radio.setProperty("value", value)
            self.orientation_group.addButton(radio)
            orientation_layout.addWidget(radio)
        
        self.orientation_group.buttons()[0].setChecked(True)
        search_layout.addLayout(orientation_layout)

        layout.addWidget(search_frame)

        # Botões de ação
        actions_layout = QHBoxLayout()
        
        self.select_folder_btn = QPushButton("Selecionar Pasta")
        self.select_folder_btn.setStyleSheet("""
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
        self.select_folder_btn.clicked.connect(self.select_output_folder)
        actions_layout.addWidget(self.select_folder_btn)
        
        self.download_btn = QPushButton("Iniciar Download")
        self.download_btn.setStyleSheet("""
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
        self.download_btn.clicked.connect(self.start_download)
        actions_layout.addWidget(self.download_btn)
        
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

    def save_api_key(self):
        api_key = self.api_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Erro", "Por favor, insira uma chave API válida.")
            return

        # Salva a chave no arquivo .env
        with open('.env', 'w') as f:
            f.write(f'PEXELS_API_KEY={api_key}')
        
        self.api_key = api_key
        QMessageBox.information(self, "Sucesso", "Chave API salva com sucesso!")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Destino",
            os.path.expanduser("~")
        )
        if folder:
            self.output_folder = folder
            self.select_folder_btn.setText(f"Pasta: {os.path.basename(folder)}")
            self.download_btn.setEnabled(True)

    def get_selected_type(self) -> str:
        return self.type_group.checkedButton().property("value")

    def get_selected_orientation(self) -> str:
        return self.orientation_group.checkedButton().property("value")

    def search_media(self) -> Optional[List[DownloadItem]]:
        print("Iniciando busca de mídia...")
        if not self.api_key:
            QMessageBox.warning(self, "Erro", "Por favor, configure sua chave API do Pexels primeiro.")
            return None
        
        # Atualiza status
        self.status_label.setText("Conectando à API do Pexels...")
        self.status_label.setStyleSheet("color: #4a90e2;")
        QApplication.processEvents()

        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Erro", "Por favor, insira um termo de busca.")
            return None

        media_type = self.get_selected_type()
        orientation = self.get_selected_orientation()

        # Define a URL base da API
        if media_type == "photos":
            url = "https://api.pexels.com/v1/search"
        else:
            url = "https://api.pexels.com/videos/search"

        # Parâmetros da busca
        params = {
            "query": query,
            "per_page": 80  # Máximo permitido pela API
        }
        if orientation:
            params["orientation"] = orientation

        headers = {"Authorization": self.api_key}

        try:
            print(f"Fazendo requisição para: {url}")
            print(f"Parâmetros: {params}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            print(f"Resposta recebida. Status: {response.status_code}")

            items = []
            if media_type == "photos":
                photos = data.get("photos", [])
                print(f"Encontradas {len(photos)} fotos")
                for photo in photos:
                    items.append(DownloadItem(
                        url=photo["src"]["original"],
                        filename=f"photo_{photo['id']}.jpg",
                        media_type="image",
                        width=photo["width"],
                        height=photo["height"]
                    ))
            else:
                videos = data.get("videos", [])
                print(f"Encontrados {len(videos)} vídeos")
                for video in videos:
                    # Pega o vídeo com maior resolução
                    video_files = sorted(
                        video["video_files"],
                        key=lambda x: x.get("width", 0) * x.get("height", 0),
                        reverse=True
                    )
                    if video_files:
                        best_video = video_files[0]
                        items.append(DownloadItem(
                            url=best_video["link"],
                            filename=f"video_{video['id']}.mp4",
                            media_type="video",
                            width=best_video.get("width", 0),
                            height=best_video.get("height", 0)
                        ))

            return items

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar mídia: {str(e)}")
            return None

    def start_download(self):
        print("\nIniciando processo de download...")
        # Verifica se a pasta de destino foi selecionada
        if not hasattr(self, 'output_folder'):
            QMessageBox.warning(self, "Erro", "Por favor, selecione uma pasta de destino primeiro.")
            return

        # Verifica se tem um termo de busca
        if not self.search_input.text().strip():
            QMessageBox.warning(self, "Erro", "Por favor, digite um termo para buscar.")
            return

        # Atualiza o status
        self.status_label.setText("Buscando mídia no Pexels...")
        self.status_label.setStyleSheet("color: #4a90e2;")
        
        # Força atualização da interface
        QApplication.processEvents()

        # Busca os itens
        items = self.search_media()
        if not items:
            self.status_label.setText("Nenhum resultado encontrado.")
            self.status_label.setStyleSheet("color: #e74c3c;")
            return
        
        # Mostra quantos itens foram encontrados
        self.status_label.setText(f"Encontrados {len(items)} itens para download.")
        self.status_label.setStyleSheet("color: #2ecc71;")

        # Desabilita os controles durante o download
        self.download_btn.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        # Inicia o download em thread separada
        self.downloader = DownloaderThread(items, self.output_folder)
        self.downloader.progress.connect(self.update_progress)
        self.downloader.error.connect(self.show_error)
        self.downloader.finished.connect(self.download_finished)
        self.downloader.item_completed.connect(self.item_downloaded)
        self.downloader.status.connect(self.update_status)
        self.downloader.start()

    def update_progress(self, current: int, total: int):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"Baixando... {current}/{total} ({progress}%)")
        self.status_label.setStyleSheet("color: #4a90e2;")
        # Força atualização da interface
        QApplication.processEvents()

    def show_error(self, message: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #e74c3c;")
        QMessageBox.warning(self, "Erro", message)

    def item_downloaded(self, filename: str):
        self.status_label.setText(f"Baixado: {os.path.basename(filename)}")
        self.status_label.setStyleSheet("color: #2ecc71;")
        # Força atualização da interface
        QApplication.processEvents()

    def download_finished(self):
        self.download_btn.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.status_label.setText("Download concluído!")
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        QMessageBox.information(self, "Sucesso", "Download concluído com sucesso!")
        self.progress_bar.hide()
        print("\nDownload finalizado com sucesso!")
