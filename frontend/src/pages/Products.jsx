import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProducts, addToCart } from "../api";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState(null);
  const navigate = useNavigate();

  const fetchCatalog = async () => {
    try {
      setLoading(true);
      const data = await getProducts();
      setProducts(data);
    } catch (err) {
      setError(err.message || "Failed to load products from server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCatalog();
  }, []);

  const handleAddToCart = async (product) => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      await addToCart(product.id, 1);
      setNotice({ type: "success", text: `"${product.name}" added to cart!` });
    } catch (err) {
      setNotice({ type: "error", text: err.message || "Could not add item to cart." });
    }

    setTimeout(() => setNotice(null), 2500);
  };

  return (
    <div>
      <div className="products-header">
        <h1>SimpleShop</h1>
        <p>Quality goods delivered right to your doorstep</p>
        {notice && (
          <div
            className={notice.type === "success" ? "alert-success" : ""}
            style={
              notice.type === "error"
                ? { color: "#ef4444", marginTop: 12, textAlign: "center", fontWeight: 500 }
                : { maxWidth: 400, margin: "16px auto" }
            }
          >
            {notice.text}
          </div>
        )}
      </div>

      {loading && <div style={{ textAlign: "center", padding: 32 }}>Loading catalog...</div>}
      {error && (
        <div style={{ color: "#ef4444", textAlign: "center", padding: 20 }}>
          {error}
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="empty-state">
          <h3>No Products Found</h3>
          <p>Check back later or add a product with an admin account.</p>
        </div>
      )}

      <div className="products-grid">
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <div>
              <h3>{product.name}</h3>
              <p>{product.description || "No description provided."}</p>
            </div>
            <div className="product-card-footer">
              <span className="product-price">${product.price.toFixed(2)}</span>
              <button
                onClick={() => handleAddToCart(product)}
                className="btn-cart"
                disabled={product.stock <= 0}
              >
                {product.stock > 0 ? "Add to cart" : "Out of Stock"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
