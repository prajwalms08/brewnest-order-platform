import { useEffect, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:9000";
const WS_URL = "ws://127.0.0.1:9000";

function Barista() {
  const [orders, setOrders] = useState([]);
  const websocketRef = useRef(null);

  const loadOrders = async () => {
    try {
      const response = await fetch(
        `${API_URL}/barista/orders/`
      );

      if (!response.ok) {
        throw new Error("Failed to load orders");
      }

      const data = await response.json();
      setOrders(data);
    } catch (error) {
      console.error(
        "Failed to load barista orders:",
        error
      );
    }
  };

  useEffect(() => {
    loadOrders();

    const websocket = new WebSocket(
      `${WS_URL}/ws/barista`
    );

    websocketRef.current = websocket;

    websocket.onopen = () => {
      console.log("Barista WebSocket connected");
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.event === "order_paid") {
        loadOrders();
      }
    };

    websocket.onclose = () => {
      console.log("Barista WebSocket disconnected");
    };

    websocket.onerror = (error) => {
      console.error(
        "Barista WebSocket error:",
        error
      );
    };

    return () => {
      websocket.close();
    };
  }, []);

  const updateStatus = async (
    orderId,
    status
  ) => {
    try {
      const response = await fetch(
        `${API_URL}/orders/${orderId}/status?status=${status}`,
        {
          method: "PATCH",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to update order"
        );
      }

      await loadOrders();
    } catch (error) {
      alert(error.message);
    }
  };

  const cancelOrder = async (orderId) => {
    const reason = window.prompt(
      "Enter cancellation reason:"
    );

    if (reason === null) {
      return;
    }

    if (!reason.trim()) {
      alert("Cancellation reason is required");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/barista/orders/${orderId}/cancel?reason=${encodeURIComponent(
          reason
        )}`,
        {
          method: "PATCH",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to cancel order"
        );
      }

      await loadOrders();
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div>
      <h1>BrewNest Barista Dashboard</h1>

      <button onClick={loadOrders}>
        Refresh Orders
      </button>

      {orders.length === 0 ? (
        <p>No paid orders available.</p>
      ) : (
        orders.map((order) => (
          <div key={order.id}>
            <h2>Order #{order.id}</h2>

            <p>
              Total: ₹{order.total_amount}
            </p>

            <p>
              Status: <strong>{order.status}</strong>
            </p>

            {order.items.map((item) => (
              <div key={item.id}>
                <p>
                  {item.item_name} × {item.quantity}
                </p>

                {item.modifiers.length > 0 && (
                  <p>
                    Modifiers:{" "}
                    {item.modifiers
                      .map(
                        (modifier) =>
                          modifier.name
                      )
                      .join(", ")}
                  </p>
                )}
              </div>
            ))}

            {order.status === "PAID" && (
              <button
                onClick={() =>
                  updateStatus(
                    order.id,
                    "PREPARING"
                  )
                }
              >
                Start Preparing
              </button>
            )}

            {order.status === "PREPARING" && (
              <>
                <button
                  onClick={() =>
                    updateStatus(
                      order.id,
                      "READY"
                    )
                  }
                >
                  Mark as Ready
                </button>

                <button
                  onClick={() =>
                    cancelOrder(order.id)
                  }
                >
                  Cancel Order
                </button>
              </>
            )}

            {order.status === "READY" && (
              <button
                onClick={() =>
                  cancelOrder(order.id)
                }
              >
                Cancel Order
              </button>
            )}

            {order.status === "CANCELLED" &&
              order.cancellation_reason && (
                <p>
                  Cancellation reason:{" "}
                  {order.cancellation_reason}
                </p>
              )}

            <hr />
          </div>
        ))
      )}
    </div>
  );
}

export default Barista;