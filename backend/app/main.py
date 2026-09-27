from fastapi import FastAPI

from app.api.routes.orders import router as orders_router


app = FastAPI(
    title="BrewNest Order Platform",
    version="1.0.0",
)


app.include_router(orders_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "BrewNest Order Platform",
    }