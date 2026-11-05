import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getCart } from "../api";

export default function Cart() {
  const [cartData, setCartData] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const loadCart = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await getCart();
      setCartData(data);
    } catch (err) {
      setError(err.message || "Failed to load cart.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCart();
  }, []);

  const token = localStorage.getItem("token");
  if (!token) {
    return (
      <div className="empty-state">
        <h3>Login Required</h3>
        <p>Please log in to view and manage your shopping cart.</p>
        <Link to="/login" className="btn-secondary">
          Go to Login
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div style={{ textAlign: "center", padding: 32 }}>Loading your cart...</div>;
  }

  if (error) {
    return <div style={{ color: "#ef4444", textAlign: "center", padding: 20 }}>{error}</div>;
  }

  if (!cartData.items || cartData.items.length === 0) {
    return (
      <div className="empty-state">
        <h3>Your Cart is Empty</h3>
        <p>You haven't added any products to your cart yet.</p>
        <Link to="/" className="btn-secondary">
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginBottom: 20 }}>Shopping Cart</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Price</th>
              <th>Quantity</th>
              <th>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {cartData.items.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>${item.price.toFixed(2)}</td>
                <td>{item.quantity}</td>
                <td>${item.subtotal.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="cart-summary">
        <div className="cart-total-label">
          Total: ${cartData.total.toFixed(2)}
        </div>
        <button
          onClick={() => navigate("/checkout")}
          className="btn-primary"
          style={{ width: "auto" }}
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
}
