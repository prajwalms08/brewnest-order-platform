import { useEffect, useRef, useState } from "react";

const API_URL = "http://127.0.0.1:9000";
const WS_URL = "ws://127.0.0.1:9000";

function CustomerStatus() {
  const [orderId, setOrderId] = useState("");
  const [order, setOrder] = useState(null);
  const [status, setStatus] = useState("");
  const [connected, setConnected] = useState(false);

  const websocketRef = useRef(null);

  const trackOrder = async () => {
    if (!orderId) {
      alert("Please enter an order ID");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/orders/${orderId}`
      );

      if (!response.ok) {
        throw new Error("Order not found");
      }

      const data = await response.json();

      setOrder(data);
      setStatus(data.status);

      if (websocketRef.current) {
        websocketRef.current.close();
      }

      const websocket = new WebSocket(
        `${WS_URL}/ws/orders/${orderId}`
      );

      websocketRef.current = websocket;

      websocket.onopen = () => {
        setConnected(true);
        console.log("WebSocket connected");
      };

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        setStatus(data.status);
      };

      websocket.onclose = () => {
        setConnected(false);
        console.log("WebSocket disconnected");
      };

      websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error(
        "Failed to track order:",
        error
      );

      alert("Order not found");
    }
  };

  const cancelOrder = async () => {
    if (!order) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/orders/${order.id}/cancel`,
        {
          method: "PATCH",
        }
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail || "Failed to cancel order"
        );
      }

      const data = await response.json();

      setStatus(data.status);

      alert("Order cancelled successfully");
    } catch (error) {
      console.error(
        "Order cancellation failed:",
        error
      );

      alert(error.message);
    }
  };

  useEffect(() => {
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, []);

  return (
    <div
      style={{
        maxWidth: "600px",
        margin: "40px auto",
        padding: "20px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Track Your Order</h1>

      <input
        type="number"
        placeholder="Enter Order ID"
        value={orderId}
        onChange={(event) =>
          setOrderId(event.target.value)
        }
        style={{
          padding: "10px",
          marginRight: "10px",
        }}
      />

      <button onClick={trackOrder}>
        Track Order
      </button>

      {order && (
        <div
          style={{
            marginTop: "30px",
            border: "1px solid #ccc",
            padding: "20px",
            borderRadius: "8px",
          }}
        >
          <h2>Order #{order.id}</h2>

          <p>
            <strong>Status:</strong>{" "}
            {status}
          </p>

          <p>
            <strong>Total:</strong> ₹
            {order.total_amount}
          </p>

          <p>
            <strong>Live Connection:</strong>{" "}
            {connected
              ? "Connected"
              : "Disconnected"}
          </p>

          {status === "CREATED" && (
            <button onClick={cancelOrder}>
              Cancel Order
            </button>
          )}

          <h3>Items</h3>

          {order.items.map((item) => (
            <p key={item.id}>
              {item.item_name} ×{" "}
              {item.quantity}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

export default CustomerStatus;