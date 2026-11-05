import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getCart, placeOrder } from "../api";

export default function Checkout() {
  const navigate = useNavigate();
  const [cartData, setCartData] = useState({ items: [], total: 0 });
  const [loadingCart, setLoadingCart] = useState(true);
  const [formData, setFormData] = useState({
    fullName: "",
    phone: "",
    address: "",
    city: "",
    postalCode: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchCheckoutCart = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        setLoadingCart(false);
        return;
      }
      try {
        const data = await getCart();
        setCartData(data);
      } catch (err) {
        setError(err.message || "Failed to load cart items.");
      } finally {
        setLoadingCart(false);
      }
    };

    fetchCheckoutCart();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    setError("");

    const { fullName, phone, address, city, postalCode } = formData;
    if (!fullName.trim() || !phone.trim() || !address.trim() || !city.trim() || !postalCode.trim()) {
      setError("Please fill in all required delivery details.");
      return;
    }

    if (!cartData.items || cartData.items.length === 0) {
      setError("Your cart is empty.");
      return;
    }

    try {
      setSubmitting(true);
      await placeOrder({
        full_name: fullName.trim(),
        phone: phone.trim(),
        address: address.trim(),
        city: city.trim(),
        postal_code: postalCode.trim(),
      });

      setSuccess(true);
      setTimeout(() => {
        navigate("/orders");
      }, 1500);
    } catch (err) {
      setError(err.message || "Failed to place order.");
    } finally {
      setSubmitting(false);
    }
  };

  const token = localStorage.getItem("token");
  if (!token) {
    return (
      <div className="empty-state">
        <h3>Login Required</h3>
        <p>Please log in to proceed with checkout.</p>
        <Link to="/login" className="btn-secondary">
          Go to Login
        </Link>
      </div>
    );
  }

  if (loadingCart) {
    return <div style={{ textAlign: "center", padding: 32 }}>Loading checkout details...</div>;
  }

  if ((!cartData.items || cartData.items.length === 0) && !success) {
    return (
      <div className="empty-state">
        <h3>Your Cart is Empty</h3>
        <p>You cannot proceed to checkout with an empty cart.</p>
        <Link to="/" className="btn-secondary">
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 650, margin: "0 auto" }}>
      <h2 style={{ marginBottom: 20 }}>Checkout</h2>

      {error && <div style={{ color: "#ef4444", marginBottom: 16 }}>{error}</div>}
      {success && (
        <div className="alert-success">
          Order placed successfully! Redirecting to My Orders...
        </div>
      )}

      {/* Order Summary */}
      <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, padding: 20, marginBottom: 24 }}>
        <h3 style={{ marginBottom: 12, fontSize: "1.1rem" }}>Order Summary</h3>
        <ul style={{ listStyle: "none", marginBottom: 12 }}>
          {cartData.items.map((item) => (
            <li key={item.id} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", fontSize: "0.9rem" }}>
              <span>{item.name} &times; {item.quantity}</span>
              <span>${item.subtotal.toFixed(2)}</span>
            </li>
          ))}
        </ul>
        <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: 8, display: "flex", justifyContent: "space-between", fontWeight: 700 }}>
          <span>Total:</span>
          <span>${cartData.total.toFixed(2)}</span>
        </div>
      </div>

      {/* Delivery Form */}
      <div className="card-box" style={{ margin: 0, maxWidth: "100%" }}>
        <h3 style={{ marginBottom: 16, fontSize: "1.1rem" }}>Delivery Details</h3>
        <form onSubmit={handlePlaceOrder}>
          <div className="form-group">
            <label htmlFor="fullName">Full Name *</label>
            <input
              id="fullName"
              name="fullName"
              type="text"
              placeholder="Jane Doe"
              value={formData.fullName}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone Number *</label>
            <input
              id="phone"
              name="phone"
              type="tel"
              placeholder="+1 (555) 000-1234"
              value={formData.phone}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="address">Street Address *</label>
            <input
              id="address"
              name="address"
              type="text"
              placeholder="123 Main Street, Apt 4B"
              value={formData.address}
              onChange={handleChange}
              required
            />
          </div>

          <div style={{ display: "flex", gap: 16 }}>
            <div className="form-group" style={{ flex: 2 }}>
              <label htmlFor="city">City *</label>
              <input
                id="city"
                name="city"
                type="text"
                placeholder="New York"
                value={formData.city}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label htmlFor="postalCode">Postal Code *</label>
              <input
                id="postalCode"
                name="postalCode"
                type="text"
                placeholder="10001"
                value={formData.postalCode}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={submitting || success}>
            {submitting ? "Placing Order..." : "Place Order"}
          </button>
        </form>
      </div>
    </div>
  );
}
