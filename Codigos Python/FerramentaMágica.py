import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import random
import datetime
from pathlib import Path
from PIL import Image, ImageTk
import sys


def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso """
    try:
        # PyInstaller cria um temp folder e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = r"C:\Users\Ernane\Desktop\Ferramentas\Phyton\Arquivos"

    return os.path.join(base_path, relative_path)


class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager - WebDark")
        self.root.geometry("800x600")
        self.selected_files = []

        # Lista de extensões de imagem suportadas
        self.image_extensions = {
            '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp',  # JPEG
            '.webp',    # WebP
            '.gif',     # GIF
            '.bmp',     # Bitmap
            '.tiff', '.tif',  # TIFF
            '.jpe',     # Outro formato JPEG
            '.heic',    # Formato Apple
            '.avif'     # AVIF
        }

        # Configure the style for modern looking widgets
        self.style = ttk.Style()
        self.style.configure("Custom.TButton",
                             background="black",
                             foreground="white",
                             padding=10,
                             font=('Helvetica', 10, 'bold'),
                             borderwidth=0,
                             relief="raised")

        # Set background color
        self.root.configure(bg='#8B0000')

        # Create main frame
        self.main_frame = tk.Frame(root, bg='#8B0000')
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Carrega e exibe a logo
        try:
            # Carrega a imagem usando o caminho absoluto
            logo_path = resource_path("Logo.jpg")
            logo_image = Image.open(logo_path)

            # Redimensiona a logo para 100x100 pixels
            logo_image = logo_image.resize(
                (100, 100), Image.Resampling.LANCZOS)

            # Converte a imagem para formato do tkinter
            self.logo_tk = ImageTk.PhotoImage(logo_image)

            # Cria e exibe o label com a logo
            logo_label = tk.Label(
                self.main_frame, image=self.logo_tk, bg='#8B0000')
            logo_label.pack(pady=10)
        except Exception as e:
            print(f"Erro ao carregar a logo: {e}")

        # Create title label
        title_label = tk.Label(self.main_frame,
                               text="File Management System",
                               font=('Helvetica', 16, 'bold'),
                               bg='#8B0000',
                               fg='white')
        title_label.pack(pady=10)

        # Create select files button
        self.select_button = tk.Button(self.main_frame,
                                       text="Selecionar Arquivos",
                                       command=self.select_files,
                                       bg='black',
                                       fg='white',
                                       font=('Helvetica', 10, 'bold'),
                                       relief='raised',
                                       width=20,
                                       height=2)
        self.select_button.pack(pady=10)

        # Create listbox to show selected files
        self.files_frame = tk.Frame(self.main_frame, bg='#8B0000')
        self.files_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.files_label = tk.Label(self.files_frame,
                                    text="Arquivos Selecionados:",
                                    font=('Helvetica', 10, 'bold'),
                                    bg='#8B0000',
                                    fg='white')
        self.files_label.pack()

        # Create scrollbar
        scrollbar = tk.Scrollbar(self.files_frame)
        scrollbar.pack(side='right', fill='y')

        # Create listbox
        self.files_listbox = tk.Listbox(self.files_frame,
                                        bg='#1a1a1a',
                                        fg='white',
                                        selectmode='extended',
                                        height=10,
                                        width=60,
                                        yscrollcommand=scrollbar.set)
        self.files_listbox.pack(pady=10)
        scrollbar.config(command=self.files_listbox.yview)

        # Create buttons frame
        buttons_frame = tk.Frame(self.main_frame, bg='#8B0000')
        buttons_frame.pack(pady=10)

        # Create action buttons lado a lado
        for text, command in [
            ("Converter para PNG", self.change_extension),
            ("Renomear Arquivos", self.rename_files),
            ("Embaralhar", self.shuffle_files)
        ]:
            button = tk.Button(buttons_frame,
                               text=text,
                               command=command,
                               bg='black',
                               fg='white',
                               font=('Helvetica', 10, 'bold'),
                               relief='raised',
                               width=20,
                               height=2)
            button.pack(side='left', padx=10)

            # Add hover effect
            button.bind("<Enter>", lambda e,
                        btn=button: btn.configure(bg='#333333'))
            button.bind("<Leave>", lambda e,
                        btn=button: btn.configure(bg='black'))

        # Create footer
        footer = tk.Label(self.main_frame,
                          text="Feito por WEBDARK",
                          font=('Helvetica', 10),
                          bg='#8B0000',
                          fg='white')
        footer.pack(side='bottom', pady=20)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Selecione os arquivos",
            filetypes=[
                ("Imagens", "*.png;*.jpg;*.jpeg;*.webp;*.gif;*.bmp;*.tiff;*.tif;*.heic;*.avif"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if files:
            # Limpa a seleção anterior
            self.selected_files.clear()
            self.files_listbox.delete(0, tk.END)

            # Adiciona os novos arquivos selecionados
            self.selected_files = list(files)
            self.update_files_listbox()

    def update_files_listbox(self):
        self.files_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.files_listbox.insert(tk.END, os.path.basename(file))

    def change_extension(self):
        if not self.selected_files:
            messagebox.showwarning(
                "Aviso", "Por favor, selecione alguns arquivos primeiro!")
            return

        try:
            files_changed = 0
            new_file_paths = []

            for file_path in self.selected_files:
                file = Path(file_path)
                if file.suffix.lower() in self.image_extensions:
                    try:
                        # Abre a imagem com PIL
                        with Image.open(file_path) as img:
                            # Prepara o novo nome do arquivo
                            new_name = file.with_suffix('.png')
                            # Salva como PNG
                            img.save(new_name, 'PNG')
                            # Se salvou com sucesso, remove o arquivo original
                            if new_name.exists():
                                file.unlink()
                                files_changed += 1
                                new_file_paths.append(str(new_name))
                    except Exception as e:
                        messagebox.showerror(
                            "Erro", f"Não foi possível converter {file.name}: {str(e)}")
                        # Mantém o arquivo original na lista
                        new_file_paths.append(file_path)
                        continue
                else:
                    # Mantém arquivos não convertíveis na lista
                    new_file_paths.append(file_path)

            # Atualiza a lista de arquivos selecionados
            self.selected_files = new_file_paths
            self.update_files_listbox()

            if files_changed > 0:
                messagebox.showinfo(
                    "Sucesso", f"{files_changed} arquivos foram convertidos para PNG!")
            else:
                messagebox.showinfo(
                    "Informação", "Nenhum arquivo foi convertido!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def rename_files(self):
        if not self.selected_files:
            messagebox.showwarning(
                "Aviso", "Por favor, selecione alguns arquivos primeiro!")
            return

        try:
            counter = 1
            directory = os.path.dirname(self.selected_files[0])
            new_file_paths = []  # Lista para armazenar os novos caminhos dos arquivos

            for file_path in sorted(self.selected_files):
                file = Path(file_path)
                new_name = Path(directory) / f"{counter}{file.suffix}"
                file.rename(new_name)
                new_file_paths.append(str(new_name))  # Armazena o novo caminho
                counter += 1

            # Atualiza a lista de arquivos selecionados com os novos caminhos
            self.selected_files = new_file_paths

            # Atualiza a listbox com os novos nomes
            self.update_files_listbox()

            messagebox.showinfo(
                "Sucesso", "Todos os arquivos foram renomeados!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def shuffle_files(self):
        if not self.selected_files:
            messagebox.showwarning(
                "Aviso", "Por favor, selecione alguns arquivos primeiro!")
            return

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            counter = 1
            directory = os.path.dirname(self.selected_files[0])
            new_file_paths = []  # Lista para armazenar os novos caminhos dos arquivos

            for file_path in self.selected_files:
                file = Path(file_path)
                random_num = random.randint(1, 10000)
                new_name = Path(directory) / \
                    f"{timestamp}_{random_num}_{counter}{file.suffix}"
                file.rename(new_name)
                new_file_paths.append(str(new_name))  # Armazena o novo caminho
                counter += 1

            # Atualiza a lista de arquivos selecionados com os novos caminhos
            self.selected_files = new_file_paths

            # Atualiza a listbox com os novos nomes
            self.update_files_listbox()

            messagebox.showinfo(
                "Sucesso", "Todos os arquivos foram embaralhados!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")


def main():
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
