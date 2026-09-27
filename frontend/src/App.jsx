import { useEffect, useState } from "react";
import Barista from "./Barista";
import CustomerStatus from "./CustomerStatus";

const API_URL = "http://127.0.0.1:9000";

function App() {
  const [menu, setMenu] = useState([]);
  const [cart, setCart] = useState([]);
  const [order, setOrder] = useState(null);
  const [orders, setOrders] = useState([]);

  // Load menu
  useEffect(() => {
    fetch(`${API_URL}/menu/`)
      .then((response) => response.json())
      .then((data) => {
        setMenu(data);
      })
      .catch((error) => {
        console.error("Failed to load menu:", error);
      });
  }, []);

  // Add item to cart
  const addToCart = (item) => {
    setCart((currentCart) => {
      const existingItem = currentCart.find(
        (cartItem) => cartItem.id === item.id
      );

      if (existingItem) {
        return currentCart.map((cartItem) =>
          cartItem.id === item.id
            ? {
                ...cartItem,
                quantity: cartItem.quantity + 1,
              }
            : cartItem
        );
      }

      return [
        ...currentCart,
        {
          ...item,
          quantity: 1,
        },
      ];
    });
  };

  // Decrease item quantity
  const decreaseQuantity = (itemId) => {
    setCart((currentCart) =>
      currentCart
        .map((item) =>
          item.id === itemId
            ? {
                ...item,
                quantity: item.quantity - 1,
              }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  };

  // Remove item from cart
  const removeFromCart = (itemId) => {
    setCart((currentCart) =>
      currentCart.filter((item) => item.id !== itemId)
    );
  };

  // Calculate cart total
  const total = cart.reduce(
    (sum, item) =>
      sum + Number(item.price) * item.quantity,
    0
  );

  // Place order
  const placeOrder = async () => {
    if (cart.length === 0) {
      alert("Cart is empty");
      return;
    }

    const orderData = {
      items: cart.map((item) => ({
        item_name: item.name,
        quantity: item.quantity,
        unit_price: Number(item.price),
      })),
    };

    try {
      const response = await fetch(`${API_URL}/orders/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        throw new Error("Failed to create order");
      }

      const data = await response.json();

      setOrder(data);
      setCart([]);

      alert(`Order #${data.id} created successfully`);
    } catch (error) {
      console.error("Order creation failed:", error);
      alert("Failed to create order");
    }
  };

  // Create Razorpay payment
  const createPayment = async () => {
    try {
      const response = await fetch(`${API_URL}/payments/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          order_id: order.id,
          amount: Number(order.total_amount),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create payment");
      }

      const payment = await response.json();

      const options = {
        key: "rzp_test_Tgz6IapCSMkZvS",

        amount: Number(order.total_amount) * 100,

        currency: "INR",

        name: "BrewNest Coffee",

        description: `Order #${order.id}`,

        order_id: payment.razorpay_order_id,

        handler: async function (response) {
          try {
            const verifyResponse = await fetch(
              `${API_URL}/payments/verify`,
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  razorpay_order_id:
                    response.razorpay_order_id,

                  razorpay_payment_id:
                    response.razorpay_payment_id,

                  razorpay_signature:
                    response.razorpay_signature,
                }),
              }
            );

            if (!verifyResponse.ok) {
              throw new Error(
                "Payment verification failed"
              );
            }

            const verifiedPayment =
              await verifyResponse.json();

            console.log(
              "Payment verified:",
              verifiedPayment
            );

            alert(
              "Payment successful and verified!"
            );
          } catch (error) {
            console.error(
              "Payment verification failed:",
              error
            );

            alert(
              "Payment verification failed"
            );
          }
        },

        theme: {
          color: "#3399cc",
        },
      };

      const razorpay =
        new window.Razorpay(options);

      razorpay.open();
    } catch (error) {
      console.error(
        "Payment creation failed:",
        error
      );

      alert("Failed to create payment");
    }
  };

  // Load order history
  const loadOrders = async () => {
    try {
      const response = await fetch(
        `${API_URL}/orders/`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load orders"
        );
      }

      const data = await response.json();

      setOrders(data);

      // Update currently displayed order
      if (order) {
        const updatedOrder = data.find(
          (item) => item.id === order.id
        );

        if (updatedOrder) {
          setOrder(updatedOrder);
        }
      }
    } catch (error) {
      console.error(
        "Failed to load orders:",
        error
      );
    }
  };

  // Barista page
  if (window.location.pathname === "/barista") {
    return <Barista />;
  }
  if (window.location.pathname === "/customer-status") {
  return <CustomerStatus />;
  } 

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "20px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>BrewNest Coffee</h1>

      {/* MENU */}
      <h2>Menu</h2>

      {menu.length === 0 ? (
        <p>No menu items available.</p>
      ) : (
        menu.map((item) => (
          <div
            key={item.id}
            style={{
              border: "1px solid #ccc",
              padding: "15px",
              marginBottom: "10px",
              borderRadius: "8px",
            }}
          >
            <h3>{item.name}</h3>

            <p>₹{item.price}</p>

            <p>{item.category}</p>

            <button
              onClick={() => addToCart(item)}
            >
              Add to Cart
            </button>
          </div>
        ))
      )}

      <hr />

      {/* CART */}
      <h2>Cart</h2>

      {cart.length === 0 ? (
        <p>Cart is empty</p>
      ) : (
        <>
          {cart.map((item) => (
            <div
              key={item.id}
              style={{
                border: "1px solid #ccc",
                padding: "15px",
                marginBottom: "10px",
                borderRadius: "8px",
              }}
            >
              <h3>{item.name}</h3>

              <p>
                ₹{item.price} × {item.quantity} = ₹
                {Number(item.price) *
                  item.quantity}
              </p>

              <button
                onClick={() =>
                  decreaseQuantity(item.id)
                }
              >
                -
              </button>

              <span
                style={{
                  margin: "0 10px",
                }}
              >
                {item.quantity}
              </span>

              <button
                onClick={() =>
                  addToCart(item)
                }
              >
                +
              </button>

              <button
                onClick={() =>
                  removeFromCart(item.id)
                }
                style={{
                  marginLeft: "10px",
                }}
              >
                Remove
              </button>
            </div>
          ))}

          <h3>Total: ₹{total}</h3>

          <button onClick={placeOrder}>
            Place Order
          </button>
        </>
      )}

      {/* CURRENT ORDER */}
      {order && (
        <>
          <hr />

          <h2>Order Created</h2>

          <div
            style={{
              border: "1px solid #ccc",
              padding: "15px",
              borderRadius: "8px",
            }}
          >
            <p>
              <strong>Order ID:</strong>{" "}
              {order.id}
            </p>

            <p>
              <strong>Status:</strong>{" "}
              {order.status}
            </p>

            <p>
              <strong>Total:</strong> ₹
              {order.total_amount}
            </p>

            <button
              onClick={createPayment}
            >
              Pay Now
            </button>
          </div>
        </>
      )}

      {/* ORDER HISTORY */}
      <hr />

      <h2>Order History</h2>

      <button onClick={loadOrders}>
        View Orders
      </button>

      {orders.length === 0 ? (
        <p>No orders found.</p>
      ) : (
        orders.map((item) => (
          <div
            key={item.id}
            style={{
              border: "1px solid #ccc",
              padding: "15px",
              marginTop: "15px",
              borderRadius: "8px",
            }}
          >
            <h3>
              Order #{item.id}
            </h3>

            <p>
              <strong>Status:</strong>{" "}
              {item.status}
            </p>

            <p>
              <strong>Total:</strong> ₹
              {item.total_amount}
            </p>

            {item.items &&
              item.items.length > 0 && (
                <div>
                  <strong>Items:</strong>

                  {item.items.map(
                    (orderItem) => (
                      <p
                        key={
                          orderItem.id
                        }
                      >
                        {orderItem.item_name} ×{" "}
                        {
                          orderItem.quantity
                        }
                      </p>
                    )
                  )}
                </div>
              )}
          </div>
        ))
      )}
    </div>
  );
}

export default App;