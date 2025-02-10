import os
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

class KiwifyAPI:
    def __init__(self):
        self.client_id = os.getenv("KIWIFY_CLIENT_ID")
        self.client_secret = os.getenv("KIWIFY_CLIENT_SECRET")
        self.account_id = os.getenv("KIWIFY_ACCOUNT_ID")
        self.base_url = "https://public-api.kiwify.com"
        self.access_token = None
        
    def get_access_token(self) -> str:
        """Gera ou retorna token OAuth existente"""
        if self.access_token:
            return self.access_token
            
        url = f"{self.base_url}/v1/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Usando o mesmo formato do curl
        data = {
            "client_secret": self.client_secret,
            "client_id": self.client_id
        }
        
        print("\nGerando token OAuth...")
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, data=data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        return self.access_token
        
    def check_purchase(self, email: str) -> Dict[str, Any]:
        """Verifica se o usuário tem compra ativa"""
        try:
            # Primeiro obtém o token
            access_token = self.get_access_token()
            
            # Decodifica o token para obter o store_id
            token_parts = access_token.split('.')
            if len(token_parts) >= 2:
                import base64
                import json
                payload = json.loads(base64.b64decode(token_parts[1] + '=' * (-len(token_parts[1]) % 4)).decode('utf-8'))
                store_id = payload.get('store_id')
            else:
                store_id = self.account_id
            
            # Configura headers conforme documentação
            headers = {
                "Authorization": f"Bearer {access_token}",
                "x-kiwify-account-id": store_id,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Busca as vendas
            sales_url = f"{self.base_url}/v1/sales"
            
            # Pega a data de hoje e 30 dias atrás
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "status": "paid"
            }
            
            print("\nBuscando vendas...")
            print(f"URL: {sales_url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            
            sales_response = requests.get(sales_url, headers=headers, params=params)
            print(f"Status code: {sales_response.status_code}")
            print(f"Response: {sales_response.text}")
            
            sales_response.raise_for_status()
            sales_data = sales_response.json()
            
            # Se email for 'all', retorna todas as vendas
            if email == "all":
                return {
                    "success": True,
                    "active": True,
                    "sales": sales_data.get("data", [])
                }
            
            # Filtra vendas pelo email do usuário
            user_sales = []
            for sale in sales_data.get("data", []):
                customer = sale.get("customer", {})
                if customer.get("email") == email:
                    user_sales.append(sale)
            
            # Verifica se há vendas ativas
            active = len(user_sales) > 0
            
            return {
                "success": True,
                "active": active,
                "sales": user_sales
            }
            params["status"] = "waiting_payment"
            pending_response = requests.get(sales_url, headers=headers, params=params)
            pending_response.raise_for_status()
            pending_data = pending_response.json()
            
            has_pending_purchase = pending_data.get('pagination', {}).get('count', 0) > 0
            
            if has_pending_purchase:
                return {"success": True, "active": False, "pending": True}
            
            return {"success": True, "active": False, "pending": False}
            
        except Exception as e:
            error_msg = f"Erro na API Kiwify: {str(e)}"
            print(f"\nErro detalhado: {error_msg}")
            return {"success": False, "error": error_msg}

class LoginManager:
    def __init__(self):
        self.kiwify = KiwifyAPI()
        
    def check_access(self, email: str) -> Dict[str, Any]:
        """
        Verifica se o usuário tem acesso ao sistema.
        Retorna um dicionário com:
        - success: bool - Se a verificação foi bem sucedida
        - active: bool - Se o usuário tem acesso ativo
        - pending: bool - Se tem compra pendente
        - error: str - Mensagem de erro (se houver)
        """
        return self.kiwify.check_purchase(email)
