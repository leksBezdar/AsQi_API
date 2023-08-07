import requests

# Замените на актуальный URL вашего API
API_URL = "http://localhost:8000"

def test_registration():
    endpoint = "/registration/"
    url = API_URL + endpoint
    data = {
        "email": "example@example.com",
        "username": "example_user",
        "hashed_password": "your_hashed_password_here",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "role_id": 1
    }

    response = requests.post(url, json=data)

    print(response.text)  # Выводим тело ответа

if __name__ == "__main__":
    test_registration()
