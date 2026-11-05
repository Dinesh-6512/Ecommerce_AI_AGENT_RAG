import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { addProduct } from "../api";

export default function AddProduct({ auth }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: "",
    stock: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const isAdmin = auth?.isAdmin ?? (localStorage.getItem("is_admin") === "true");

  if (!isAdmin) {
    return (
      <div className="empty-state">
        <h3 style={{ color: "#ef4444" }}>Access Denied</h3>
        <p>This screen is restricted to administrators only.</p>
      </div>
    );
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const { name, description, price, stock } = formData;
    if (!name.trim() || !price || !stock) {
      setError("Please fill in Name, Price, and Stock.");
      return;
    }

    try {
      setSubmitting(true);
      await addProduct({
        name: name.trim(),
        description: description.trim(),
        price,
        stock,
      });

      setSuccess(true);
      setTimeout(() => {
        navigate("/");
      }, 1200);
    } catch (err) {
      setError(err.message || "Failed to add product.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card-box">
      <h2>Add New Product</h2>
      {error && <div style={{ color: "#ef4444", marginBottom: 12 }}>{error}</div>}
      {success && (
        <div className="alert-success">
          Product created successfully! Redirecting to catalog...
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Product Name *</label>
          <input
            id="name"
            name="name"
            type="text"
            placeholder="e.g. Leather Wallet"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            rows="3"
            placeholder="Detailed description of the product"
            value={formData.description}
            onChange={handleChange}
          />
        </div>

        <div style={{ display: "flex", gap: 16 }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label htmlFor="price">Price ($) *</label>
            <input
              id="price"
              name="price"
              type="number"
              step="0.01"
              min="0"
              placeholder="29.99"
              value={formData.price}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group" style={{ flex: 1 }}>
            <label htmlFor="stock">Stock Quantity *</label>
            <input
              id="stock"
              name="stock"
              type="number"
              min="0"
              placeholder="100"
              value={formData.stock}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={submitting || success}>
          {submitting ? "Saving Product..." : "Save Product"}
        </button>
      </form>
    </div>
  );
}
