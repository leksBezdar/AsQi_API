from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")



ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS")



MIN_USERNAME_LENGTH = os.environ.get("MIN_USERNAME_LENGTH")
MAX_USERNAME_LENGTH = os.environ.get("MAX_USERNAME_LENGTH")

MIN_PASSWORD_LENGTH = os.environ.get("MIN_PASSWORD_LENGTH")
MAX_PASSWORD_LENGTH = os.environ.get("MAX_PASSWORD_LENGTH")