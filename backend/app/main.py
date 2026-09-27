from fastapi import FastAPI

from app.api.routes.menu import router as menu_router
from app.api.routes.orders import router as orders_router
from app.api.routes.payments import router as payments_router


app = FastAPI(
    title="BrewNest Order Platform",
    version="1.0.0",
)


app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(menu_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "BrewNest Order Platform",
    }