from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.barista import router as barista_router
from app.api.routes.menu import router as menu_router
from app.api.routes.orders import router as orders_router
from app.api.routes.payments import router as payments_router
from app.websocket.manager import manager


app = FastAPI(
    title="BrewNest Order Platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(menu_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(barista_router)


@app.get("/")
def root():
    return {
        "message": "BrewNest Order Platform API"
    }


@app.websocket("/ws/orders/{order_id}")
async def order_status_websocket(
    websocket: WebSocket,
    order_id: int,
):
    await manager.connect_order(
        order_id,
        websocket,
    )

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect_order(
            order_id,
            websocket,
        )


@app.websocket("/ws/barista")
async def barista_websocket(
    websocket: WebSocket,
):
    await manager.connect_barista(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect_barista(websocket)