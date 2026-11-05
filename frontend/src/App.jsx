import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Products from "./pages/Products";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import MyOrders from "./pages/MyOrders";
import AddProduct from "./pages/AddProduct";
import Chat from "./pages/Chat";

export default function App() {
  const [auth, setAuth] = useState(() => ({
    token: localStorage.getItem("token") || null,
    isAdmin: localStorage.getItem("is_admin") === "true",
  }));

  const handleLogin = (authData) => {
    setAuth(authData);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("is_admin");
    setAuth({ token: null, isAdmin: false });
  };

  return (
    <>
      <Navbar auth={auth} onLogout={handleLogout} />
      <main className="container">
        <Routes>
          <Route path="/" element={<Products />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/orders" element={<MyOrders />} />
          <Route path="/admin/add-product" element={<AddProduct auth={auth} />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
      <Footer />
    </>
  );
}
