import os
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class AuthManager:
    def __init__(self):
        # Inicializa cliente Supabase
        url: str = os.getenv("SUPABASE_URL", "")
        key: str = os.getenv("SUPABASE_KEY", "")
        self.supabase: Client = create_client(url, key)
        self.current_user = None
        
    def check_email(self, email: str) -> Dict[str, Any]:
        """
        Verifica se o email já existe no Supabase.
        Retorna: {"exists": bool, "user": dict or None}
        """
        try:
            print(f"\nVerificando email: {email}")
            print(f"URL Supabase: {self.supabase.supabase_url}")
            
            # Tentar fazer login com uma senha inválida para ver se o usuário existe
            try:
                self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": "_check_only_"
                })
                # Se chegou aqui, deu certo o login (não deveria acontecer)
                return {"exists": True, "user": None}
            except Exception as auth_error:
                error_message = str(auth_error)
                if "Invalid login credentials" in error_message:
                    # Se deu erro de credenciais inválidas, significa que o email não existe
                    print("Email não existe no Auth")
                    return {"exists": False, "user": None}
                else:
                    # Se deu outro erro, assumimos que o email existe
                    print("Email existe no Auth")
                    return {"exists": True, "user": None}
            
        except Exception as e:
            print(f"Erro ao verificar email: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"exists": False, "user": None}
    
    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """
        Cria uma nova conta.
        """
        try:
            print(f"\nTentando criar conta para: {email}")
            
            # 1. Tentar fazer login primeiro (caso o usuário já exista)
            try:
                print("Tentando fazer login primeiro...")
                login_response = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                print("Login realizado com sucesso!")
                self.current_user = login_response.user
                
                # Verificar se precisa criar registro na tabela users
                check = self.check_email(email)
                if not check["exists"]:
                    print("Criando registro na tabela users...")
                    user_data = {
                        "id": login_response.user.id,
                        "email": email,
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    }
                    
                    self.supabase.table("users").insert(user_data).execute()
                    print("Registro criado com sucesso!")
                else:
                    print("Registro já existe na tabela users")
                
                # Retorna is_new_account=False pois é um login
                return {"success": True, "user": login_response.user, "is_new_account": False}
                
            except Exception as login_error:
                print(f"Login falhou, tentando criar nova conta: {str(login_error)}")
                
                # 2. Se o login falhar, tentar criar nova conta
                auth_response = self.supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                
                if not auth_response.user:
                    print("Erro ao criar usuário no Supabase Auth")
                    return {"success": False, "error": "Erro ao criar usuário"}
                
                print("Conta criada, fazendo login...")
                # 3. Fazer login para obter token
                login_response = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if not login_response.user:
                    print("Erro ao fazer login após criar conta")
                    return {"success": False, "error": "Erro ao fazer login após criar conta"}
                
                print("Login realizado, criando registro na tabela users...")
                # 4. Criar registro na tabela users
                user_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
                
                self.supabase.table("users").insert(user_data).execute()
                self.current_user = login_response.user
                
                print("Conta criada com sucesso!")
                # Retorna is_new_account=True pois é uma nova conta
                return {"success": True, "user": login_response.user, "is_new_account": True}
            
        except Exception as e:
            print(f"Erro ao criar conta: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Faz login com email e senha.
        """
        try:
            print(f"\nTentando fazer login com: {email}")
            
            # 1. Verificar se o usuário existe na tabela users
            check = self.check_email(email)
            if not check["exists"]:
                print("Usuário não encontrado na tabela users")
                return {"success": False, "error": "Usuário não encontrado"}
            
            print("Usuário encontrado, verificando senha...")
            # 2. Tentar fazer login no Auth
            try:
                auth_response = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if auth_response.user:
                    print("Login realizado com sucesso!")
                    self.current_user = auth_response.user
                    return {"success": True, "user": auth_response.user}
                
                print("Credenciais inválidas")
                return {"success": False, "error": "Credenciais inválidas"}
                
            except Exception as auth_error:
                print(f"Erro ao fazer login: {str(auth_error)}")
                return {"success": False, "error": "Senha incorreta"}
            
        except Exception as e:
            print(f"Erro ao fazer login: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def get_user_status(self, email: str) -> str:
        """
        Retorna o status do usuário: active, inactive
        """
        try:
            response = self.supabase.table("users").select("status").eq("email", email).execute()
            return response.data[0]["status"] if response.data else "inactive"
        except Exception:
            return "inactive"
    
    def sign_out(self) -> None:
        """
        Faz logout do usuário atual.
        """
        try:
            self.supabase.auth.sign_out()
            self.current_user = None
        except Exception as e:
            print(f"Erro ao fazer logout: {str(e)}")
