from app.integrations.mongodb import MongoDBClient


class MenuRepository:

    def __init__(self):
        self.mongodb = MongoDBClient()
        self.collection = self.mongodb.get_collection("menu")

    def get_menu(self):
        menu_items = list(
            self.collection.find({})
        )

        for item in menu_items:
            item["id"] = str(item.pop("_id"))

        return menu_items

    def create_menu_item(self, menu_item: dict):
        document = menu_item.copy()

        document["price"] = float(document["price"])

        result = self.collection.insert_one(document)

        document.pop("_id", None)
        document["id"] = str(result.inserted_id)

        return document