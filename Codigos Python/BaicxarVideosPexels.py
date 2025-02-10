#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para baixar imagens ou vídeos da API Pexels
Desenvolvido para WEBDARK
Versão atualizada para:
 - Baixar todos os resultados da busca (usando paginação)
 - Mostrar o progresso e permitir interromper o download
 - Filtrar vídeos para baixar apenas os de tamanho grande (largura >= LARGE_VIDEO_THRESHOLD)
 - Se algum download ficar travado por mais de 30 segundos (read timeout), informar ao usuário que o download terminou e parar o processo.
"""

import os
import json
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Arquivo de configuração para salvar a API key
CONFIG_FILE = "config.json"
# Limiar para considerar um vídeo "grande" (em pixels de largura)
LARGE_VIDEO_THRESHOLD = 1920

def load_config():
    """Carrega a configuração (ex.: API key) se existir."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(config):
    """Salva a configuração em um arquivo JSON."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def download_media(url, filename, stop_event, timeout_callback=None):
    """
    Faz o download do arquivo (imagem/vídeo) e o salva em 'filename'.
    Se o stop_event for acionado ou se o download ficar sem receber dados por mais de 30 segundos,
    o processo é interrompido.
    """
    try:
        # timeout: 5 segundos para conexão e 30 segundos para leitura
        response = requests.get(url, stream=True, timeout=(5, 30))
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if stop_event.is_set():
                    return False  # Interrompe se o usuário pediu para parar
                if chunk:
                    f.write(chunk)
        return True
    except requests.exceptions.ReadTimeout:
        # Se a leitura travar por mais de 30 segundos, interpretamos como fim do download.
        if timeout_callback:
            timeout_callback()
        stop_event.set()
        return False
    except Exception as e:
        print("Erro ao baixar:", e)
        return False

def buscar_e_baixar(api_key, search_type, orientation, query, download_folder, stop_event, progress_callback, timeout_callback):
    """
    Realiza a busca via API e baixa os resultados na pasta escolhida.
    Itera pelas páginas disponíveis e atualiza o progresso via callback.
    Para vídeos, baixa apenas aqueles que possuam uma versão com largura >= LARGE_VIDEO_THRESHOLD.
    """
    headers = {"Authorization": api_key}
    if search_type == "imagens":
        base_url = "https://api.pexels.com/v1/search"
        result_key = "photos"
    elif search_type == "videos":
        base_url = "https://api.pexels.com/videos/search"
        result_key = "videos"
    else:
        messagebox.showerror("Erro", "Tipo de busca inválido.")
        return

    per_page = 80  # máximo permitido pela API
    page = 1
    total_downloaded = 0
    total_results = None

    while not stop_event.is_set():
        params = {"query": query, "per_page": per_page, "page": page}
        if orientation in ["landscape", "portrait"]:
            params["orientation"] = orientation

        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=(5, 30))
            response.raise_for_status()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na requisição: {e}")
            break

        data = response.json()
        if total_results is None:
            total_results = data.get("total_results", 0)
        results = data.get(result_key, [])
        if not results:
            break  # não há mais resultados

        for item in results:
            if stop_event.is_set():
                break
            if search_type == "imagens":
                img_url = item.get("src", {}).get("original")
                if not img_url:
                    continue
                ext = os.path.splitext(img_url)[-1]
                file_path = os.path.join(download_folder, f"imagem_{total_downloaded+1}{ext}")
                if download_media(img_url, file_path, stop_event, timeout_callback):
                    total_downloaded += 1
                    progress_callback(total_downloaded, total_results)
            else:
                video_files = item.get("video_files", [])
                if not video_files:
                    continue
                # Ordena os arquivos por largura (ordem decrescente)
                video_files_sorted = sorted(video_files, key=lambda x: x.get("width", 0), reverse=True)
                # Seleciona o primeiro arquivo com largura >= LARGE_VIDEO_THRESHOLD
                selected_video = None
                for vf in video_files_sorted:
                    if vf.get("width", 0) >= LARGE_VIDEO_THRESHOLD:
                        selected_video = vf
                        break
                if selected_video is None:
                    continue  # nenhum arquivo "grande" disponível para este vídeo
                video_url = selected_video.get("link")
                if not video_url:
                    continue
                file_path = os.path.join(download_folder, f"video_{total_downloaded+1}.mp4")
                if download_media(video_url, file_path, stop_event, timeout_callback):
                    total_downloaded += 1
                    progress_callback(total_downloaded, total_results)

        # Se o número de resultados nesta página for menor que o máximo, chegou à última página
        if len(results) < per_page:
            break
        page += 1

    if stop_event.is_set():
        # Se o stop_event foi ativado, significa que ou o usuário interrompeu
        # ou um timeout ocorreu (o callback já exibiu uma mensagem)
        messagebox.showinfo("Download Interrompido", f"Download interrompido.\nArquivos baixados: {total_downloaded}")
    else:
        if total_downloaded > 0:
            messagebox.showinfo("Sucesso", f"{total_downloaded} arquivo(s) baixado(s) na pasta:\n{download_folder}")
        else:
            messagebox.showerror("Erro", "Nenhum arquivo foi baixado.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Downloader Pexels - WEBDARK")
        self.geometry("500x550")
        self.resizable(False, False)
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        # Flag para indicar se houve timeout
        self.timed_out = False

        # Variáveis para controle do download
        self.download_thread = None
        self.stop_event = None

        self.create_widgets()
        self.load_saved_api()

    def create_widgets(self):
        padding = {'padx': 10, 'pady': 10}

        # --- Frame para inserir a chave API ---
        api_frame = ttk.LabelFrame(self, text="Chave API do Pexels")
        api_frame.pack(fill="x", **padding)
        self.api_key_var = tk.StringVar()
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.api_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50)
        self.api_entry.grid(row=0, column=1, padx=5, pady=5)
        self.save_api_btn = ttk.Button(api_frame, text="Salvar Chave", command=self.salvar_api)
        self.save_api_btn.grid(row=0, column=2, padx=5, pady=5)

        # --- Frame para opções de busca ---
        options_frame = ttk.LabelFrame(self, text="Opções de Busca")
        options_frame.pack(fill="x", **padding)
        self.search_type_var = tk.StringVar(value="imagens")
        ttk.Label(options_frame, text="Tipo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tipo_frame = ttk.Frame(options_frame)
        tipo_frame.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(tipo_frame, text="Imagens", variable=self.search_type_var, value="imagens").pack(side="left", padx=5)
        ttk.Radiobutton(tipo_frame, text="Vídeos", variable=self.search_type_var, value="videos").pack(side="left", padx=5)

        self.orientation_var = tk.StringVar(value="landscape")
        ttk.Label(options_frame, text="Orientação:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        orient_frame = ttk.Frame(options_frame)
        orient_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(orient_frame, text="Horizontal", variable=self.orientation_var, value="landscape").pack(side="left", padx=5)
        ttk.Radiobutton(orient_frame, text="Vertical", variable=self.orientation_var, value="portrait").pack(side="left", padx=5)

        ttk.Label(options_frame, text="Busca (em inglês):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.busca_var = tk.StringVar()
        self.busca_entry = ttk.Entry(options_frame, textvariable=self.busca_var, width=50)
        self.busca_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- Frame para selecionar a pasta de destino ---
        folder_frame = ttk.LabelFrame(self, text="Pasta de Destino")
        folder_frame.pack(fill="x", **padding)
        self.folder_var = tk.StringVar()
        ttk.Label(folder_frame, text="Salvar em:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=40)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5)
        self.choose_folder_btn = ttk.Button(folder_frame, text="Escolher Pasta", command=self.choose_folder)
        self.choose_folder_btn.grid(row=0, column=2, padx=5, pady=5)

        # --- Botões para iniciar e parar o download ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        self.download_btn = ttk.Button(btn_frame, text="Buscar e Baixar", command=self.iniciar_busca)
        self.download_btn.pack(side="left", padx=10)
        self.stop_download_btn = ttk.Button(btn_frame, text="Parar Download", command=self.parar_download, state="disabled")
        self.stop_download_btn.pack(side="left", padx=10)

        self.progress_label = ttk.Label(self, text="Download: 0 / ?")
        self.progress_label.pack(pady=10)
        self.direitos_label = ttk.Label(self, text="© WEBDARK", font=("Arial", 10))
        self.direitos_label.pack(side="bottom", pady=5)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de destino")
        if folder:
            self.folder_var.set(folder)

    def salvar_api(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Erro", "Por favor, insira a chave API.")
            return
        config = load_config()
        config["api_key"] = api_key
        save_config(config)
        messagebox.showinfo("Sucesso", "Chave API salva com sucesso!")

    def load_saved_api(self):
        config = load_config()
        if "api_key" in config:
            self.api_key_var.set(config["api_key"])

    def handle_timeout(self):
        """Callback chamado quando um download fica travado por mais de 30 segundos."""
        self.timed_out = True
        self.after(0, lambda: messagebox.showinfo("Download Finalizado", 
                        "Download finalizado, arquivo parado por mais de 30 segundos."))

    def iniciar_busca(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Erro", "Por favor, insira a chave API.")
            return
        search_type = self.search_type_var.get()
        orientation = self.orientation_var.get()
        query = self.busca_var.get().strip()
        if not query:
            messagebox.showerror("Erro", "Por favor, insira o termo de busca.")
            return
        download_folder = self.folder_var.get().strip()
        if not download_folder:
            messagebox.showerror("Erro", "Por favor, escolha a pasta de destino para salvar os arquivos.")
            return

        self.timed_out = False
        self.stop_event = threading.Event()
        self.progress_label.config(text="Download: 0 / ?")
        self.download_btn.config(state="disabled")
        self.stop_download_btn.config(state="normal")

        self.download_thread = threading.Thread(
            target=self.start_download_thread,
            args=(api_key, search_type, orientation, query, download_folder, self.stop_event)
        )
        self.download_thread.start()

    def start_download_thread(self, api_key, search_type, orientation, query, download_folder, stop_event):
        buscar_e_baixar(api_key, search_type, orientation, query, download_folder, stop_event, self.update_progress, self.handle_timeout)
        self.after(0, self.download_finished)

    def update_progress(self, count, total):
        self.after(0, lambda: self.progress_label.config(text=f"Download: {count} de {total} arquivo(s) baixados"))

    def download_finished(self):
        self.download_btn.config(state="normal")
        self.stop_download_btn.config(state="disabled")

    def parar_download(self):
        if self.stop_event:
            self.stop_event.set()
            self.stop_download_btn.config(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
