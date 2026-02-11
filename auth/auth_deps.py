import os
from dotenv import load_dotenv
from authx import AuthX, AuthXConfig

# Загружаем переменные из .env файла
load_dotenv()

# Получаем API ключ из переменных окружения
MY_API_KEY = os.getenv("MY_API_KEY", "default_api_key")

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET", "SECRET_KEY")  # Безопасный ключ из .env
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['cookies', 'headers']
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_DECODE_ALGORITHMS = ["HS256"]

security = AuthX(config=config,)