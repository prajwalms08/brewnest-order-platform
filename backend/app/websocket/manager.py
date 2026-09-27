from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(
        self,
        order_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        self.active_connections[order_id] = websocket

    def disconnect(self, order_id: int):
        self.active_connections.pop(
            order_id,
            None,
        )

    async def send_status(
        self,
        order_id: int,
        status: str,
    ):
        websocket = self.active_connections.get(
            order_id
        )

        if websocket:
            await websocket.send_json(
                {
                    "order_id": order_id,
                    "status": status,
                }
            )


manager = ConnectionManager()