import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:9000";

function Barista() {
  const [orders, setOrders] = useState([]);

  const loadOrders = async () => {
    try {
      const response = await fetch(
        `${API_URL}/orders/`
      );

      if (!response.ok) {
        throw new Error("Failed to load orders");
      }

      const data = await response.json();

      setOrders(data);
    } catch (error) {
      console.error(
        "Failed to load orders:",
        error
      );
    }
  };

  useEffect(() => {
    loadOrders();
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

      if (!response.ok) {
        throw new Error(
          "Failed to update order"
        );
      }

      await loadOrders();
    } catch (error) {
      console.error(
        "Failed to update status:",
        error
      );
    }
  };

  return (
    <div>
      <h1>BrewNest Barista Dashboard</h1>

      <button onClick={loadOrders}>
        Refresh Orders
      </button>

      {orders.length === 0 ? (
        <p>No orders available.</p>
      ) : (
        orders.map((order) => (
          <div
            key={order.id}
            style={{
              border: "1px solid #ccc",
              padding: "15px",
              marginTop: "15px",
              borderRadius: "8px",
            }}
          >
            <h2>
              Order #{order.id}
            </h2>

            <p>
              <strong>Status:</strong>{" "}
              {order.status}
            </p>

            <p>
              <strong>Total:</strong> ₹
              {order.total_amount}
            </p>

            <h3>Items</h3>

            {order.items &&
              order.items.map((item) => (
                <p key={item.id}>
                  {item.item_name} ×{" "}
                  {item.quantity}
                </p>
              ))}

            {order.status === "CREATED" && (
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
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default Barista;