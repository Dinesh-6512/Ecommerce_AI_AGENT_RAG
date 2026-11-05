import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getMyOrders } from "../api";

export default function MyOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadOrders = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await getMyOrders();
      setOrders(data);
    } catch (err) {
      setError(err.message || "Failed to load orders.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const token = localStorage.getItem("token");
  if (!token) {
    return (
      <div className="empty-state">
        <h3>Login Required</h3>
        <p>Please log in to view your orders.</p>
        <Link to="/login" className="btn-secondary">
          Go to Login
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div style={{ textAlign: "center", padding: 32 }}>Loading your orders...</div>;
  }

  if (error) {
    return <div style={{ color: "#ef4444", textAlign: "center", padding: 20 }}>{error}</div>;
  }

  if (orders.length === 0) {
    return (
      <div className="empty-state">
        <h3>No Orders Yet</h3>
        <p>You haven't placed any orders yet.</p>
        <Link to="/" className="btn-secondary">
          Start Shopping
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginBottom: 20 }}>My Orders</h2>
      <div className="orders-list">
        {orders.map((order) => {
          const formattedDate = order.created_at
            ? new Date(order.created_at).toLocaleDateString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
              })
            : "Recent";

          return (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <div>
                  <strong>Order #{order.id}</strong>
                  <span style={{ color: "#64748b", marginLeft: 12, fontSize: "0.875rem" }}>
                    {formattedDate}
                  </span>
                </div>
                <div>
                  <span className="order-badge">{order.status}</span>
                </div>
              </div>

              <ul className="order-items-list">
                {order.items &&
                  order.items.map((item) => (
                    <li key={item.id} className="order-item-row">
                      <span>
                        {item.product_name} &times; {item.quantity}
                      </span>
                      <span>${(item.price * item.quantity).toFixed(2)}</span>
                    </li>
                  ))}
              </ul>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  borderTop: "1px solid #f1f5f9",
                  paddingTop: 8,
                  fontWeight: 700,
                }}
              >
                <span>Total Amount:</span>
                <span>${Number(order.total).toFixed(2)}</span>
              </div>

              <div className="order-delivery">
                <strong>Delivery Address:</strong> {order.full_name} | {order.phone}
                <br />
                {order.address}, {order.city}, {order.postal_code}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
