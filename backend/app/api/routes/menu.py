from fastapi import APIRouter

from app.schemas.menu import MenuCreate, MenuResponse
from app.services.menu_service import MenuService


router = APIRouter(prefix="/menu", tags=["Menu"])

menu_service = MenuService()


@router.get("/", response_model=list[MenuResponse])
def get_menu():
    return menu_service.get_menu()


@router.post("/", response_model=MenuResponse)
def create_menu_item(menu_item: MenuCreate):
    return menu_service.create_menu_item(
        menu_item.model_dump()
    )