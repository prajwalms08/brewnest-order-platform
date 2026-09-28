import { useEffect, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:9000";
const WS_URL = "ws://127.0.0.1:9000";

function CustomerStatus() {
  const [orderId, setOrderId] = useState("");
  const [order, setOrder] = useState(null);
  const [status, setStatus] = useState("");
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");

  const websocketRef = useRef(null);
  const pollingRef = useRef(null);

  const loadOrder = async (id) => {
    try {
      const response = await fetch(`${API_URL}/orders/${id}`);

      if (!response.ok) {
        throw new Error("No order exists.");
      }

      const data = await response.json();

      setOrder(data);
      setStatus(data.status);
      setError("");
    } catch (error) {
      setOrder(null);
      setStatus("");
      setError(error.message);
    }
  };

  const trackOrder = async () => {
    if (!orderId) {
      setError("Please enter an order ID.");
      return;
    }

    if (websocketRef.current) {
      websocketRef.current.close();
    }

    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }

    await loadOrder(orderId);

    const websocket = new WebSocket(
      `${WS_URL}/ws/orders/${orderId}`
    );

    websocketRef.current = websocket;

    websocket.onopen = () => {
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.event === "order_status") {
        setStatus(data.status);

        setOrder((previousOrder) => {
          if (!previousOrder) {
            return previousOrder;
          }

          return {
            ...previousOrder,
            status: data.status,
          };
        });
      }
    };

    websocket.onclose = () => {
      setConnected(false);
    };

    websocket.onerror = () => {
      setConnected(false);
    };

    pollingRef.current = setInterval(() => {
      loadOrder(orderId);
    }, 2000);
  };

  const cancelOrder = async () => {
    try {
      const response = await fetch(
        `${API_URL}/orders/${orderId}/cancel`,
        {
          method: "PATCH",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to cancel order"
        );
      }

      setStatus(data.status);

      setOrder((previousOrder) => ({
        ...previousOrder,
        status: data.status,
      }));

      setError("");
    } catch (error) {
      setError(error.message);
    }
  };

  useEffect(() => {
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }

      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  return (
    <div>
      <h1>Customer Order Status</h1>

      <input
        type="number"
        placeholder="Enter Order ID"
        value={orderId}
        onChange={(event) =>
          setOrderId(event.target.value)
        }
      />

      <button onClick={trackOrder}>
        Track Order
      </button>

      {error && (
        <p>
          <strong>{error}</strong>
        </p>
      )}

      {order && (
        <div>
          <h2>Order #{order.id}</h2>

          <p>
            Total: ₹{order.total_amount}
          </p>

          <p>
            Status: <strong>{status}</strong>
          </p>

          <p>
            Live connection:{" "}
            {connected ? "Connected" : "Disconnected"}
          </p>

          {status === "CANCELLED" &&
            order.cancellation_reason && (
              <p>
                <strong>
                  Cancellation reason:
                </strong>{" "}
                {order.cancellation_reason}
              </p>
            )}

          {(status === "CREATED" ||
            status === "PAID") && (
            <button onClick={cancelOrder}>
              Cancel Order
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default CustomerStatus;