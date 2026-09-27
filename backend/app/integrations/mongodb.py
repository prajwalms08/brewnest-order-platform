from pymongo import MongoClient

from app.core.config import settings


class MongoDBClient:

    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.database = self.client[settings.MONGODB_DATABASE]

    def get_collection(self, collection_name: str):
        return self.database[collection_name]