import os
from auth.auth_manager import KiwifyAPI
from datetime import datetime, timedelta
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def get_token(api):
    """Obter token de acesso"""
    url = f"{api.base_url}/v1/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "client_id": os.getenv("KIWIFY_CLIENT_ID"),
        "client_secret": api.client_secret,
        "grant_type": "client_credentials"
    }
    
    print("\nURL:", url)
    print("Headers:", json.dumps(headers, indent=2))
    print("Data:", json.dumps(data, indent=2))
    
    response = requests.post(url, headers=headers, data=data)
    print(f"\nStatus: {response.status_code}")
    print("Response:", response.text)
    
    if response.ok:
        token_data = response.json()
        token = token_data.get("access_token")
        if token:
            print("\nToken obtido com sucesso!")
            return token
    raise Exception(f"Erro ao obter token: {response.text}")

def get_sales(api, email):
    """Buscar vendas do usuário"""
    all_sales = []
    end_date = datetime.now()
    
    # Buscar vendas em períodos de 90 dias
    for i in range(4):  # Últimos 360 dias (4 x 90)
        start_date = end_date - timedelta(days=90)
        
        url = f"{api.base_url}/v1/sales"
        headers = api.get_headers()
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        print(f"\nBuscando período {i+1}/4:")
        print("URL:", url)
        print("Headers:", json.dumps(headers, indent=2))
        print("Params:", json.dumps(params, indent=2))
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print("\nVendas encontradas neste período:")
            for sale in data.get("data", []):
                customer = sale.get("customer", {})
                product = sale.get("product", {})
                print(f"\nVenda ID: {sale.get('id')}")
                print(f"Status: {sale.get('status')}")
                print(f"Data: {sale.get('created_at')}")
                print(f"Cliente: {customer.get('name')} ({customer.get('email')})")
                print(f"Produto: {product.get('name')}")
            
            # Filtrar vendas pelo email
            sales = [
                sale for sale in data.get("data", [])
                if sale.get("customer", {}).get("email") == email
            ]
            all_sales.extend(sales)
        else:
            print(f"Erro na busca: {response.text}")
        
        end_date = start_date - timedelta(days=1)
    
    return {"data": all_sales}

def test_kiwify_purchase():
    print("Iniciando teste de compra Kiwify...")
    api = KiwifyAPI()
    email = "gutembergmendes526@gmail.com"
    
    try:
        # 1. Obter token
        print("\n1. Obtendo token de acesso...")
        token = get_token(api)
        api.access_token = token
        
        # 2. Buscar vendas
        print(f"\n2. Buscando vendas para {email}...")
        data = get_sales(api, email)
        
        # 3. Analisar vendas
        print("\n3. Analisando vendas...")
        print("\nResposta da API:")
        print(json.dumps(data, indent=2))
        
        active_sales = [
            sale for sale in data.get("data", [])
            if sale.get("status") in ["paid", "pending"]
        ]
        
        if active_sales:
            print(f"\nEncontradas {len(active_sales)} vendas ativas!")
            for sale in active_sales:
                print(f"\nVenda ID: {sale.get('id')}")
                print(f"Status: {sale.get('status')}")
                print(f"Data: {sale.get('created_at')}")
                print(f"Produto: {sale.get('product', {}).get('name')}")
        else:
            print("\nNenhuma venda ativa encontrada.")
            
    except Exception as e:
        print(f"\nErro: {str(e)}")

if __name__ == "__main__":
    test_kiwify_purchase()
