from flask import Flask, render_template, jsonify, request
import webview
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
window = None

# Inicializa Supabase
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        global auth_success
        auth_success = True
        window.destroy()  # Fecha a janela após login bem sucedido
        return jsonify({"success": True})
    except Exception as e:
        print(f"[DEBUG] Erro no login: {str(e)}")
        return jsonify({"success": False})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        # Primeiro verifica se o email já existe
        try:
            supabase.auth.sign_in_with_password({
                "email": email,
                "password": "senha_invalida_para_teste"
            })
            # Se chegou aqui, o email já existe
            return jsonify({"success": False, "error": "Este email já está cadastrado"})
        except:
            # Se deu erro, o email não existe, podemos criar a conta
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            global auth_success
            auth_success = True
            window.destroy()  # Fecha a janela após cadastro bem sucedido
            return jsonify({"success": True})
    except Exception as e:
        print(f"[DEBUG] Erro no signup: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

auth_success = False

def show_auth_window():
    global window, auth_success
    auth_success = False
    
    # Inicia o servidor Flask em uma thread
    window = webview.create_window('WebDark Studio', app, width=400, height=600)
    webview.start()
    
    return auth_success  # Retorna se a autenticação foi bem sucedida

if __name__ == '__main__':
    show_auth_window()
