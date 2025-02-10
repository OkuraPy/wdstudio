from auth.login_manager import KiwifyAPI
from datetime import datetime

def format_currency(amount):
    # Converte centavos para reais
    return f"R$ {amount/100:.2f}"

def format_date(date_str):
    # Converte data UTC para local
    date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date.strftime("%d/%m/%Y %H:%M:%S")

# Email para testar
TEST_EMAIL = "pbfelipealmeida@gmail.com"

# Instancia API
api = KiwifyAPI()

# Obtém token
api.get_access_token()

# Busca vendas
result = api.check_purchase(TEST_EMAIL)

if result["success"] and result.get("sales"):
    print("\nÚltimas 10 vendas:")
    print("-" * 80)
    
    for sale in result["sales"][:10]:
        customer = sale["customer"]
        product = sale["product"]
        
        print(f"Data: {format_date(sale['created_at'])}")
        print(f"Cliente: {customer['name']}")
        print(f"Email: {customer['email']}")
        print(f"Produto: {product['name']}")
        if product.get('plan_name'):
            print(f"Plano: {product['plan_name']}")
        print(f"Valor: {format_currency(sale['net_amount'])}")
        print(f"Método: {sale['payment_method']}")
        print("-" * 80)
else:
    print("Erro ao buscar vendas:", result.get("error", "Erro desconhecido"))
