import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!name.trim() || !email.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    try {
      setLoading(true);
      await registerUser({ name, email, password });
      setMessage("Account created successfully! Redirecting to login...");
      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (err) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-card">
      <h2>Register</h2>
      {error && <div style={{ color: "#ef4444", marginBottom: 12, textAlign: "center" }}>{error}</div>}
      {message && <div className="alert-success">{message}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Full Name</label>
          <input
            id="name"
            type="text"
            placeholder="John Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            placeholder="user@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Creating Account..." : "Register"}
        </button>
      </form>
      <div className="auth-footer">
        Already have an account? <Link to="/login">Login here</Link>
      </div>
    </div>
  );
}
