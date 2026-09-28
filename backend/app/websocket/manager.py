from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.order_connections: dict[int, set[WebSocket]] = {}
        self.barista_connections: set[WebSocket] = set()

    async def connect_order(
        self,
        order_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if order_id not in self.order_connections:
            self.order_connections[order_id] = set()

        self.order_connections[order_id].add(websocket)

    def disconnect_order(
        self,
        order_id: int,
        websocket: WebSocket,
    ):
        connections = self.order_connections.get(order_id)

        if connections:
            connections.discard(websocket)

            if not connections:
                self.order_connections.pop(order_id)

    async def send_status(
        self,
        order_id: int,
        status: str,
    ):
        connections = self.order_connections.get(
            order_id,
            set(),
        )

        message = {
            "event": "order_status",
            "order_id": order_id,
            "status": status,
        }

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect_order(
                order_id,
                websocket,
            )

    async def connect_barista(
        self,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.barista_connections.add(websocket)

    def disconnect_barista(
        self,
        websocket: WebSocket,
    ):
        self.barista_connections.discard(websocket)

    async def broadcast_barista(
        self,
        order_id: int,
    ):
        message = {
            "event": "order_paid",
            "order_id": order_id,
            "status": "PAID",
        }

        disconnected = []

        for websocket in self.barista_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect_barista(websocket)


manager = ConnectionManager()