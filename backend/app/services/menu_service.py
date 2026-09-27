from app.repositories.menu_repository import MenuRepository


class MenuService:

    def __init__(self):
        self.repository = MenuRepository()

    def get_menu(self):
        return self.repository.get_menu()

    def create_menu_item(self, menu_item: dict):
        return self.repository.create_menu_item(menu_item)