import os
import jwt
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class KiwifyAPI:
    """Classe para interagir com a API da Kiwify"""
    
    def __init__(self):
        self.base_url = "https://public-api.kiwify.com"
        self.client_id = os.getenv("KIWIFY_CLIENT_ID")
        self.client_secret = os.getenv("KIWIFY_CLIENT_SECRET")
        self.access_token = None
        self.account_id = None
        
    def get_access_token(self) -> str:
        """Obtém um token de acesso OAuth"""
        if self.access_token:
            return self.access_token
            
        url = f"{self.base_url}/v1/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, headers=headers, data=data)
        if response.ok:
            data = response.json()
            self.access_token = data["access_token"]
            
            # Extrair store_id do token JWT
            token_data = jwt.decode(self.access_token, options={"verify_signature": False})
            self.account_id = token_data.get("store_id")
            
            return self.access_token
        raise Exception(f"Erro ao obter token: {response.text}")
    
    def get_headers(self) -> Dict[str, str]:
        """Retorna os headers necessários para as requisições"""
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "x-kiwify-account-id": self.account_id,
            "Accept": "application/json"
        }
    
    def get_sales(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Busca vendas em um período específico
        
        Args:
            start_date: Data inicial
            end_date: Data final (máximo 90 dias após start_date)
            
        Returns:
            Lista de vendas encontradas
        """
        if (end_date - start_date).days > 90:
            raise ValueError("O período entre start_date e end_date não pode ser maior que 90 dias")
            
        url = f"{self.base_url}/v1/sales"
        headers = self.get_headers()
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.ok:
            return response.json().get("data", [])
        raise Exception(f"Erro ao buscar vendas: {response.text}")
    
    def find_customer_purchases(self, email: str, days: int = 360) -> List[Dict]:
        """
        Busca todas as compras de um cliente pelo email
        
        Args:
            email: Email do cliente
            days: Quantidade de dias para buscar no histórico (default: 360)
            
        Returns:
            Lista de compras do cliente
        """
        all_purchases = []
        end_date = datetime.now()
        
        # Buscar em períodos de 90 dias
        while days > 0:
            period = min(90, days)
            start_date = end_date - timedelta(days=period)
            
            try:
                sales = self.get_sales(start_date, end_date)
                # Filtrar vendas pelo email
                customer_sales = [
                    sale for sale in sales
                    if sale.get("customer", {}).get("email") == email
                ]
                all_purchases.extend(customer_sales)
            except Exception as e:
                print(f"Erro ao buscar período {start_date} a {end_date}: {str(e)}")
            
            end_date = start_date - timedelta(days=1)
            days -= period
            
        return all_purchases
    
    def has_active_purchase(self, email: str) -> bool:
        """
        Verifica se o cliente tem alguma compra ativa
        
        Args:
            email: Email do cliente
            
        Returns:
            True se tiver alguma compra paga e não reembolsada
        """
        purchases = self.find_customer_purchases(email)
        return any(
            purchase.get("status") == "paid"
            for purchase in purchases
        )
