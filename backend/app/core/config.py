import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "BrewNest Order Platform")
    APP_ENV = os.getenv("APP_ENV", "development")

    DATABASE_URL = os.getenv("DATABASE_URL")

    MONGODB_URL = os.getenv("MONGODB_URL")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")


settings = Settings()