import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import threading
from datetime import datetime

class AudioProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Removedor de Silêncio")
        
        # Configuração do ffmpeg - CAMINHO ABSOLUTO
        self.FFMPEG_PATH = r"C:\Users\Ernane\Desktop\Ferramentas\Phyton\Removedor de Silencio Audio\ffmpeg-7.1\bin"
        
        # Verifica se o ffmpeg existe
        if not self.check_ffmpeg():
            messagebox.showerror("Erro", f"FFmpeg não encontrado em:\n{self.FFMPEG_PATH}\n\nVerifique se o caminho está correto.")
            root.destroy()
            return
        
        # Configura o ffmpeg
        self.configure_ffmpeg()
        
        # Variáveis
        self.input_file = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto para processar")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Criação da interface
        self.create_widgets()
        
        # Centraliza a janela
        self.center_window(500, 400)
    
    def check_ffmpeg(self):
        """Verifica se os arquivos do ffmpeg existem"""
        ffmpeg_exe = os.path.join(self.FFMPEG_PATH, "ffmpeg.exe")
        ffprobe_exe = os.path.join(self.FFMPEG_PATH, "ffprobe.exe")
        return os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe)
    
    def configure_ffmpeg(self):
        """Configura o ffmpeg no sistema"""
        # Adiciona ffmpeg ao PATH
        if self.FFMPEG_PATH not in os.environ["PATH"]:
            os.environ["PATH"] = self.FFMPEG_PATH + os.pathsep + os.environ["PATH"]
        
        # Configura variáveis de ambiente
        os.environ['FFMPEG_BINARY'] = os.path.join(self.FFMPEG_PATH, 'ffmpeg.exe')
        os.environ['FFPROBE_BINARY'] = os.path.join(self.FFMPEG_PATH, 'ffprobe.exe')
        
        # Configura pydub
        AudioSegment.converter = os.path.join(self.FFMPEG_PATH, "ffmpeg.exe")
        AudioSegment.ffmpeg = os.path.join(self.FFMPEG_PATH, "ffmpeg.exe")
        AudioSegment.ffprobe = os.path.join(self.FFMPEG_PATH, "ffprobe.exe")
        
    def create_widgets(self):
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Removedor de Silêncio", 
                              font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Frame para seleção de arquivo
        file_frame = ttk.LabelFrame(main_frame, text="Seleção de Arquivo", padding="5")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Campo de arquivo
        self.file_entry = ttk.Entry(file_frame, textvariable=self.input_file, width=50)
        self.file_entry.grid(row=0, column=0, padx=5, pady=5)
        
        # Botão de navegação
        browse_btn = ttk.Button(file_frame, text="Procurar", command=self.browse_file)
        browse_btn.grid(row=0, column=1, padx=5)
        
        # Frame para configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="5")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configurações de silêncio
        ttk.Label(config_frame, text="Duração mínima do silêncio (ms):").grid(row=0, column=0, padx=5, pady=2)
        self.silence_len = ttk.Entry(config_frame, width=10)
        self.silence_len.insert(0, "1000")
        self.silence_len.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Threshold de silêncio (dB):").grid(row=1, column=0, padx=5, pady=2)
        self.silence_thresh = ttk.Entry(config_frame, width=10)
        self.silence_thresh.insert(0, "-40")
        self.silence_thresh.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Silêncio nas extremidades (ms):").grid(row=2, column=0, padx=5, pady=2)
        self.keep_silence = ttk.Entry(config_frame, width=10)
        self.keep_silence.insert(0, "100")
        self.keep_silence.grid(row=2, column=1, padx=5, pady=2)
        
        # Botão de processamento
        self.process_btn = ttk.Button(main_frame, text="Processar Áudio", 
                                    command=self.start_processing)
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                      maximum=100, length=300, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Status
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
            
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Arquivos de áudio", "*.mp3 *.wav"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            
    def update_status(self, message, progress=None):
        self.status_var.set(message)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()
        
    def process_audio(self):
        try:
            input_file = self.input_file.get()
            if not input_file:
                messagebox.showerror("Erro", "Selecione um arquivo de áudio!")
                return
            
            self.update_status("Verificando ffmpeg...", 5)
            
            # Verifica novamente o ffmpeg
            if not self.check_ffmpeg():
                raise Exception(f"FFmpeg não encontrado em: {self.FFMPEG_PATH}")
            
            # Criação da pasta de saída
            output_dir = os.path.join(os.path.dirname(input_file), "Audio novo")
            os.makedirs(output_dir, exist_ok=True)
            
            # Define arquivo de saída
            filename = os.path.basename(input_file)
            base_name, ext = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{base_name}_sem_silencio{ext}")
            
            self.update_status("Carregando arquivo...", 10)
            
            # Carrega o áudio
            if input_file.lower().endswith('.mp3'):
                audio = AudioSegment.from_mp3(input_file)
            else:
                audio = AudioSegment.from_wav(input_file)
            
            self.update_status("Detectando silêncio...", 30)
            
            # Processa o áudio
            chunks = split_on_silence(
                audio,
                min_silence_len=int(self.silence_len.get()),
                silence_thresh=int(self.silence_thresh.get()),
                keep_silence=int(self.keep_silence.get())
            )
            
            if not chunks:
                messagebox.showwarning("Aviso", "Nenhum trecho de áudio detectado! Tente ajustar os parâmetros.")
                self.update_status("Pronto para processar", 0)
                return
            
            self.update_status("Combinando áudio...", 60)
            
            # Combina os chunks
            combined = chunks[0]
            for chunk in chunks[1:]:
                combined += chunk
            
            self.update_status("Salvando arquivo...", 80)
            
            # Salva o resultado
            combined.export(output_file, format=ext[1:])
            
            self.update_status("Concluído com sucesso!", 100)
            messagebox.showinfo("Sucesso", 
                              f"Arquivo processado com sucesso!\nSalvo em: {output_file}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante o processamento:\n{str(e)}\n\nCaminho do FFmpeg: {self.FFMPEG_PATH}")
            self.update_status("Erro no processamento", 0)
        
        finally:
            self.process_btn.config(state='normal')
            
    def start_processing(self):
        self.process_btn.config(state='disabled')
        self.update_status("Iniciando processamento...", 0)
        # Inicia o processamento em uma thread separada
        threading.Thread(target=self.process_audio, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioProcessorGUI(root)
    root.mainloop()