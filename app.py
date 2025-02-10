from flask import Flask, render_template, jsonify, request
import webview
import threading
from tools import (
    image_converter,
    video_cutter,
    pexels_downloader,
    silence_remover,
    subtitle_generator,
    folder_creator
)

app = Flask(__name__)

class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        print('Configurando janela para a API')
        self.window = window

    def choose_folder(self):
        print('Chamando choose_folder')
        try:
            result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
            print('Pasta selecionada:', result)
            return result[0] if result else ''
        except Exception as e:
            print('Erro ao selecionar pasta:', str(e))
            return ''

    def choose_files(self):
        print('Chamando choose_files')
        try:
            result = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True)
            print('Arquivos selecionados:', result)
            return result if result else []
        except Exception as e:
            print('Erro ao selecionar arquivos:', str(e))
            return []

@app.route('/')
def index():
    return render_template('index.html')

# Variável global para armazenar o progresso
progress_data = {
    'current': 0,
    'total': 0,
    'message': ''
}

def reset_progress():
    """Reseta os dados de progresso para o estado inicial"""
    global progress_data
    progress_data = {
        'current': 0,
        'total': 0,
        'message': ''
    }

@app.route('/download-progress')
def get_progress():
    return jsonify(progress_data)

@app.route('/download-video', methods=['POST'])
def download_video():
    try:
        # Reseta o progresso no início de um novo download
        reset_progress()
        
        query = request.form.get('query')
        path = request.form.get('path')
        limit = request.form.get('limit')

        # Converte o limite para inteiro se fornecido
        if limit:
            try:
                limit = int(limit)
                if limit < 1:
                    return jsonify({"success": False, "error": "O limite deve ser maior que zero"})
            except ValueError:
                return jsonify({"success": False, "error": "O limite deve ser um número válido"})

        # Função de callback para atualizar o progresso
        def update_progress(current, total, message):
            global progress_data
            progress_data['current'] = current
            progress_data['total'] = total
            progress_data['message'] = message

        # Inicia o download com o callback de progresso
        result = pexels_downloader.download_videos(query, path, limit, progress_callback=update_progress)
        
        # Após o download, reseta o progresso
        if result.get('success'):
            # Aguarda um momento antes de resetar para que o cliente possa ver 100%
            from time import sleep
            sleep(3)
            reset_progress()
            
        return jsonify(result)
    except Exception as e:
        # Em caso de erro, reseta o progresso
        reset_progress()
        return jsonify({"success": False, "error": str(e)})

@app.route('/convert-images', methods=['POST'])
def convert_images():
    try:
        source = request.form.get('source')
        target = request.form.get('target')
        image_converter.convert_images(source, target)
        return jsonify({"success": True, "message": "Imagens convertidas com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/cut-video', methods=['POST'])
def cut_video():
    try:
        path = request.form.get('path')
        duration = int(request.form.get('duration', 10))  # default 10 segundos
        video_cutter.cut_videos(path, duration)
        return jsonify({"success": True, "message": "Vídeos cortados com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/remove-silence', methods=['POST'])
def remove_silence():
    try:
        file_path = request.form.get('file')
        silence_remover.remove_silence(file_path)
        return jsonify({"success": True, "message": "Silêncio removido com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/generate-subtitles', methods=['POST'])
def generate_subtitles():
    try:
        video_path = request.form.get('video')
        subtitle_generator.generate_srt(video_path)
        return jsonify({"success": True, "message": "Legendas geradas com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/create-folders', methods=['POST'])
def create_folders():
    try:
        base_path = request.form.get('path')
        folder_creator.create_month_folders(base_path)
        return jsonify({"success": True, "message": "Pastas criadas com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def start_server():
    app.run(port=5000)

if __name__ == '__main__':
    # Inicia o servidor Flask em uma thread separada
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Cria a API
    api = Api()
    
    # Cria a janela desktop
    window = webview.create_window(
        'WebDark Studio', 
        'http://127.0.0.1:5000',
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600),
        resizable=True
    )
    
    api.set_window(window)
    webview.start()
