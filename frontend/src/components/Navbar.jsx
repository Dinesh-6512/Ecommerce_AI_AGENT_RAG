import React from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

export default function Navbar({ auth, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) onLogout();
    navigate("/login");
  };

  return (
    <header className="header">
      <div className="nav-container">
        <Link to="/" className="brand">
          SimpleShop
        </Link>
        <nav>
          <ul className="nav-links">
            <li>
              <NavLink to="/" end>
                Products
              </NavLink>
            </li>

            {auth.token ? (
              <>
                <li>
                  <NavLink to="/cart">Cart</NavLink>
                </li>
                <li>
                  <NavLink to="/orders">My Orders</NavLink>
                </li>
                <li>
                  <NavLink to="/chat">Chat</NavLink>
                </li>
                {auth.isAdmin && (
                  <li>
                    <NavLink to="/admin/add-product">Add Product</NavLink>
                  </li>
                )}
                <li>
                  <button onClick={handleLogout} className="btn-link">
                    Logout
                  </button>
                </li>
              </>
            ) : (
              <>
                <li>
                  <NavLink to="/chat">Chat</NavLink>
                </li>
                <li>
                  <NavLink to="/login">Login</NavLink>
                </li>
                <li>
                  <NavLink to="/register">Register</NavLink>
                </li>
              </>
            )}
          </ul>
        </nav>
      </div>
    </header>
  );
}
