import { useEffect, useState } from "react";
import Barista from "./Barista";
import CustomerStatus from "./CustomerStatus";

const API_URL = "http://127.0.0.1:9000";

function App() {
  const [menu, setMenu] = useState([]);
  const [cart, setCart] = useState([]);
  const [order, setOrder] = useState(null);
  const [orders, setOrders] = useState([]);
  const [selectedModifiers, setSelectedModifiers] = useState({});

  useEffect(() => {
    fetch(`${API_URL}/menu/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load menu");
        }

        return response.json();
      })
      .then((data) => {
        setMenu(data);
      })
      .catch((error) => {
        console.error("Failed to load menu:", error);
      });
  }, []);

  const toggleModifier = (itemId, modifier) => {
    setSelectedModifiers((current) => {
      const currentModifiers = current[itemId] || [];

      const alreadySelected = currentModifiers.some(
        (selected) => selected.name === modifier.name
      );

      if (alreadySelected) {
        return {
          ...current,
          [itemId]: currentModifiers.filter(
            (selected) => selected.name !== modifier.name
          ),
        };
      }

      return {
        ...current,
        [itemId]: [...currentModifiers, modifier],
      };
    });
  };

  const addToCart = (item) => {
    const modifiers = selectedModifiers[item.id] || [];

    const modifierTotal = modifiers.reduce(
      (sum, modifier) => sum + Number(modifier.price),
      0
    );

    const itemPrice =
      Number(item.price) + modifierTotal;

    const modifierKey = modifiers
      .map((modifier) => modifier.name)
      .sort()
      .join("-");

    const cartKey = `${item.id}-${modifierKey}`;

    setCart((currentCart) => {
      const existingItem = currentCart.find(
        (cartItem) => cartItem.cartKey === cartKey
      );

      if (existingItem) {
        return currentCart.map((cartItem) =>
          cartItem.cartKey === cartKey
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
          modifiers,
          itemPrice,
          cartKey,
        },
      ];
    });

    setSelectedModifiers((current) => ({
      ...current,
      [item.id]: [],
    }));
  };

  const increaseQuantity = (cartItem) => {
    setCart((currentCart) =>
      currentCart.map((item) =>
        item.cartKey === cartItem.cartKey
          ? {
              ...item,
              quantity: item.quantity + 1,
            }
          : item
      )
    );
  };

  const decreaseQuantity = (cartKey) => {
    setCart((currentCart) =>
      currentCart
        .map((item) =>
          item.cartKey === cartKey
            ? {
                ...item,
                quantity: item.quantity - 1,
              }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  };

  const removeFromCart = (cartKey) => {
    setCart((currentCart) =>
      currentCart.filter(
        (item) => item.cartKey !== cartKey
      )
    );
  };

  const total = cart.reduce(
    (sum, item) =>
      sum + item.itemPrice * item.quantity,
    0
  );

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
        modifiers: item.modifiers.map((modifier) => ({
          name: modifier.name,
          price: Number(modifier.price),
        })),
      })),
    };

    try {
      const response = await fetch(
        `${API_URL}/orders/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(orderData),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to create order");
      }

      const data = await response.json();

      setOrder(data);
      setCart([]);

      alert(
        `Order #${data.id} created successfully`
      );
    } catch (error) {
      console.error(
        "Order creation failed:",
        error
      );

      alert("Failed to create order");
    }
  };

  const createPayment = async () => {
    if (!order) {
      alert("No order available for payment");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/payments/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            order_id: order.id,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail ||
            "Failed to create payment"
        );
      }

      const payment = await response.json();

      const options = {
        // Keep your existing Razorpay TEST Key ID here.
        key: "rzp_test_Tgz6IapCSMkZvS",

        amount:
          Number(payment.amount) * 100,

        currency: "INR",

        name: "BrewNest Coffee",

        description: `Order #${order.id}`,

        order_id:
          payment.razorpay_order_id,

        handler: function () {
          alert(
            "Payment submitted. Waiting for payment confirmation."
          );
        },

        modal: {
          ondismiss: function () {
            console.log(
              "Razorpay checkout closed"
            );
          },
        },

        theme: {
          color: "#6f4e37",
        },
      };

      if (!window.Razorpay) {
        throw new Error(
          "Razorpay Checkout script is not loaded"
        );
      }

      const razorpay =
        new window.Razorpay(options);

      razorpay.open();
    } catch (error) {
      console.error(
        "Payment creation failed:",
        error
      );

      alert(error.message);
    }
  };

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

  if (
    window.location.pathname ===
    "/barista"
  ) {
    return <Barista />;
  }

  if (
    window.location.pathname ===
    "/customer-status"
  ) {
    return <CustomerStatus />;
  }

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "20px",
        fontFamily:
          "Arial, sans-serif",
      }}
    >
      <h1>BrewNest Coffee</h1>

      <h2>Menu</h2>

      {menu.length === 0 ? (
        <p>No menu items available.</p>
      ) : (
        menu.map((item) => (
          <div
            key={item.id}
            style={{
              border: "1px solid #ddd",
              padding: "18px",
              marginBottom: "15px",
              borderRadius: "10px",
              backgroundColor: "#fff",
            }}
          >
            <h3>{item.name}</h3>

            <p>
              <strong>
                Base Price:
              </strong>{" "}
              ₹{item.price}
            </p>

            <p>{item.category}</p>

            {item.modifiers &&
              item.modifiers.length > 0 && (
                <div>
                  <h4>Modifiers</h4>

                  {item.modifiers.map(
                    (modifier) => {
                      const isSelected =
                        (
                          selectedModifiers[
                            item.id
                          ] || []
                        ).some(
                          (selected) =>
                            selected.name ===
                            modifier.name
                        );

                      return (
                        <label
                          key={
                            modifier.name
                          }
                          style={{
                            display:
                              "block",
                            marginBottom:
                              "8px",
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={
                              isSelected
                            }
                            onChange={() =>
                              toggleModifier(
                                item.id,
                                modifier
                              )
                            }
                          />

                          {" "}

                          {
                            modifier.name
                          }{" "}
                          (+₹
                          {
                            modifier.price
                          })
                        </label>
                      );
                    }
                  )}
                </div>
              )}

            <button
              onClick={() =>
                addToCart(item)
              }
            >
              Add to Cart
            </button>
          </div>
        ))
      )}

      <hr />

      <h2>Cart</h2>

      {cart.length === 0 ? (
        <p>Cart is empty</p>
      ) : (
        <>
          {cart.map((item) => (
            <div
              key={item.cartKey}
              style={{
                border:
                  "1px solid #ddd",
                padding: "15px",
                marginBottom: "10px",
                borderRadius: "8px",
                backgroundColor:
                  "#fff",
              }}
            >
              <h3>{item.name}</h3>

              <p>
                Base price: ₹
                {item.price}
              </p>

              {item.modifiers &&
                item.modifiers.length > 0 && (
                  <div>
                    <strong>
                      Modifiers:
                    </strong>

                    {item.modifiers.map(
                      (modifier) => (
                        <p
                          key={
                            modifier.name
                          }
                        >
                          {
                            modifier.name
                          }{" "}
                          +₹
                          {
                            modifier.price
                          }
                        </p>
                      )
                    )}
                  </div>
                )}

              <p>
                ₹{item.itemPrice} ×{" "}
                {item.quantity} = ₹
                {item.itemPrice *
                  item.quantity}
              </p>

              <button
                onClick={() =>
                  decreaseQuantity(
                    item.cartKey
                  )
                }
              >
                -
              </button>

              <span
                style={{
                  margin:
                    "0 10px",
                }}
              >
                {item.quantity}
              </span>

              <button
                onClick={() =>
                  increaseQuantity(item)
                }
              >
                +
              </button>

              <button
                onClick={() =>
                  removeFromCart(
                    item.cartKey
                  )
                }
                style={{
                  marginLeft:
                    "10px",
                }}
              >
                Remove
              </button>
            </div>
          ))}

          <h3>
            Total: ₹{total}
          </h3>

          <button
            onClick={placeOrder}
          >
            Place Order
          </button>
        </>
      )}

      {order && (
        <>
          <hr />

          <h2>Order Created</h2>

          <div
            style={{
              border:
                "1px solid #ddd",
              padding: "18px",
              borderRadius: "8px",
              backgroundColor:
                "#fff",
            }}
          >
            <p>
              <strong>
                Order ID:
              </strong>{" "}
              {order.id}
            </p>

            <p>
              <strong>
                Status:
              </strong>{" "}
              {order.status}
            </p>

            <p>
              <strong>
                Total:
              </strong>{" "}
              ₹{order.total_amount}
            </p>

            <button
              onClick={createPayment}
            >
              Pay Now
            </button>
          </div>
        </>
      )}

      <hr />

      <h2>Order History</h2>

      <button
        onClick={loadOrders}
      >
        View Orders
      </button>

      {orders.length === 0 ? (
        <p>No orders found.</p>
      ) : (
        orders.map((item) => (
          <div
            key={item.id}
            style={{
              border:
                "1px solid #ddd",
              padding: "15px",
              marginTop: "15px",
              borderRadius: "8px",
              backgroundColor:
                "#fff",
            }}
          >
            <h3>
              Order #{item.id}
            </h3>

            <p>
              <strong>
                Status:
              </strong>{" "}
              {item.status}
            </p>

            <p>
              <strong>
                Total:
              </strong>{" "}
              ₹{item.total_amount}
            </p>

            <strong>
              Items:
            </strong>

            {item.items &&
              item.items.map(
                (orderItem) => (
                  <div
                    key={
                      orderItem.id
                    }
                  >
                    <p>
                      {
                        orderItem.item_name
                      }{" "}
                      ×{" "}
                      {
                        orderItem.quantity
                      }
                    </p>

                    {orderItem.modifiers &&
                      orderItem
                        .modifiers
                        .length >
                        0 && (
                        <div
                          style={{
                            marginLeft:
                              "20px",
                          }}
                        >
                          <strong>
                            Modifiers:
                          </strong>

                          {orderItem.modifiers.map(
                            (
                              modifier
                            ) => (
                              <p
                                key={
                                  modifier.name
                                }
                              >
                                {
                                  modifier.name
                                }{" "}
                                +₹
                                {
                                  modifier.price
                                }
                              </p>
                            )
                          )}
                        </div>
                      )}
                  </div>
                )
              )}
          </div>
        ))
      )}
    </div>
  );
}

export default App;