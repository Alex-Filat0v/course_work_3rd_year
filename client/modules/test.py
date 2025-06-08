import urllib.request
import json
import socket
from datetime import date


def test_with_urllib():
    url = "http://127.0.0.1:8000/registrations"

    # Данные для отправки
    auth_data = {
        "surname": "Urllib",
        "first_name": "Test",
        "patronymic": "Client",
        "mail": "urllib@test.com",
        "phone_number": "79001112233",
        "birth_date": "2003-04-16",
        "username": "urllib_user2",  # Убедитесь, что логин новый
        "password": "password123"
    }

    # Преобразуем словарь в байты JSON
    data = json.dumps(auth_data).encode('utf-8')

    # Создаем объект запроса
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    # --- Важный момент: отключаем прокси для urllib ---
    # Создаем обработчик, который не использует прокси
    proxy_handler = urllib.request.ProxyHandler({})
    # Создаем "открыватель" URL с этим обработчиком
    opener = urllib.request.build_opener(proxy_handler)

    print(f"--- Тест с urllib ---")
    print(f"Отправка запроса на: {url}")
    print("Прокси отключены.")

    try:
        # Используем наш "открыватель" для выполнения запроса
        with opener.open(req, timeout=10) as response:
            # Если мы дошли до сюда, соединение установлено!
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')

            print(f"✅ УСПЕХ! Сервер ответил.")
            print(f"Статус код: {status_code}")
            print(f"Тело ответа: {response_body}")

    except urllib.error.HTTPError as e:
        # Сервер ответил ошибкой (например, 401, 404, 503)
        print(f"❌ ОШИБКА HTTP: Сервер ответил с ошибкой.")
        print(f"Статус код: {e.code}")
        print(f"Тело ответа: {e.read().decode('utf-8', errors='ignore')}")

    except urllib.error.URLError as e:
        # Не удалось подключиться к серверу (connection refused, timeout, etc.)
        print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: Не удалось соединиться с сервером.")
        print(f"Причина: {e.reason}")

    except socket.timeout:
        print("❌ ОШИБКА: Таймаут подключения. Сервер не ответил вовремя.")

    except Exception as e:
        print(f"❌ НЕИЗВЕСТНАЯ ОШИБКА: {type(e).__name__} - {e}")


if __name__ == "__main__":
    test_with_urllib()