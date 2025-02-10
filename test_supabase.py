from auth.auth_manager import AuthManager

def test_supabase():
    print("Inicializando AuthManager...")
    auth = AuthManager()
    
    print("\nTestando conexão com Supabase...")
    try:
        # Tenta buscar a configuração do Supabase
        response = auth.supabase.auth.get_session()
        print("Conexão com Supabase estabelecida com sucesso!")
        
        # Tenta criar um usuário real
        email = "rodrigochagasicm@gmail.com"
        password = "WebDark@2024"
        
        print(f"\nTentando criar usuário: {email}")
        result = auth.supabase.auth.sign_up({
            "email": email,
            "password": password,
            "data": {
                "name": "Rodrigo Chagas",
                "email": email
            }
        })
        print("\nUsuário criado com sucesso!")
        print("Por favor, verifique seu email para confirmar o cadastro.")
        print("\nDados para login:")
        print(f"Email: {email}")
        print(f"Senha: {password}")
        
    except Exception as e:
        print("Erro:", str(e))

if __name__ == "__main__":
    test_supabase()
