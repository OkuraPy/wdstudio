import time
from auth.auth_manager import AuthManager

def test_auth():
    print("Iniciando teste de autenticação...")
    auth = AuthManager()
    
    # Dados de teste
    email = "teste.auth@gmail.com"
    password = "senha123"
    
    try:
        # 1. Verificar se email existe
        print("\n1. Verificando email...")
        check = auth.check_email(email)
        print(f"Email existe? {check['exists']}")
        
        if check['exists']:
            print("Conta já existe, tentando login...")
            time.sleep(10)  # Delay maior            
            # Fazer login
            print("\n2. Fazendo login...")
            login_result = auth.sign_in(email, password)
            print(f"Login realizado: {login_result['success']}")
            if not login_result['success']:
                print(f"Erro no login: {login_result['error']}")
                return
                
        else:
            print("Conta não existe, criando nova conta...")
            time.sleep(10)  # Delay maior            
            # Criar nova conta
            print("\n2. Criando nova conta...")
            signup_result = auth.sign_up(email, password)
            print(f"Conta criada: {signup_result['success']}")
            if not signup_result['success']:
                print(f"Erro ao criar conta: {signup_result['error']}")
                return
                
            print("\nAguardando 15 segundos antes de fazer login...")
            time.sleep(15)  # Delay maior após criar conta
            
            # Fazer primeiro login
            print("\n3. Fazendo primeiro login...")
            login_result = auth.sign_in(email, password)
            print(f"Login realizado: {login_result['success']}")
            if not login_result['success']:
                print(f"Erro no primeiro login: {login_result['error']}")
                return
        
        time.sleep(5)  # Delay médio
        
        # Verificar status
        print("\n4. Verificando status do usuário...")
        status = auth.get_user_status(email)
        print(f"Status: {status}")
        
        time.sleep(5)  # Delay médio
        
        # Fazer logout
        print("\n5. Fazendo logout...")
        auth.sign_out()
        print("Logout realizado com sucesso!")
        
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")

if __name__ == "__main__":
    test_auth()
