from auth.login_manager import LoginManager

def test_kiwify():
    login_manager = LoginManager()
    email = "pbfelipealmeida@gmail.com"
    
    print(f"\nVerificando compra para o email: {email}")
    result = login_manager.check_access(email)
    
    print("\nResultado:")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_kiwify()
