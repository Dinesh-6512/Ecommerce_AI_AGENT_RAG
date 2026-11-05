import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please fill in email and password.");
      return;
    }

    try {
      setLoading(true);
      const data = await loginUser({ email, password });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("is_admin", data.is_admin ? "true" : "false");

      if (onLogin) {
        onLogin({ token: data.access_token, isAdmin: data.is_admin });
      }

      navigate("/");
    } catch (err) {
      setError(err.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-card">
      <h2>Login</h2>
      {error && <div style={{ color: "#ef4444", marginBottom: 12, textAlign: "center" }}>{error}</div>}
      <form onSubmit={handleSubmit}>
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
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <div className="auth-footer">
        Don't have an account? <Link to="/register">Register here</Link>
      </div>
    </div>
  );
}
