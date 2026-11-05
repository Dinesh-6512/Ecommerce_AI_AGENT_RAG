import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { sendChatMessage } from "../api";

const AVAILABLE_MANUALS = [
  { name: "Classic White T-Shirt", file: "classic-white-t-shirt.pdf" },
  { name: "Wireless Bluetooth Headphones", file: "wireless-bluetooth-headphones.pdf" },
  { name: "Stainless Steel Water Bottle", file: "stainless-steel-water-bottle.pdf" },
  { name: "Canvas Everyday Backpack", file: "canvas-everyday-backpack.pdf" },
  { name: "Ceramic Coffee Mug", file: "ceramic-coffee-mug.pdf" },
];

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      sender: "assistant",
      text: "Hello! I am your SimpleShop assistant. How can I help you today? You can ask about our products, your cart, past orders, or questions from product manuals (how to use, troubleshooting, and warranty).",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showManualsShelf, setShowManualsShelf] = useState(true);
  const messagesEndRef = useRef(null);

  const token = localStorage.getItem("token");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const question = (textToSend || input).trim();
    if (!question || loading) return;

    const userMessage = { sender: "user", text: question, sources: [] };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(question);
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: err.message || "Sorry, I was unable to complete your request. Please try again in a moment.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend();
  };

  if (!token) {
    return (
      <div className="empty-state">
        <h3>Login Required</h3>
        <p>Please log in to chat with the Shop Assistant.</p>
        <Link to="/login" className="btn-secondary">
          Go to Login
        </Link>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div>
          <h2>Shop Assistant</h2>
          <p>One assistant for store catalog, your cart, orders, and product manuals</p>
        </div>
        <button
          type="button"
          onClick={() => setShowManualsShelf(!showManualsShelf)}
          className="btn-secondary"
          style={{ fontSize: "0.75rem", padding: "4px 8px" }}
        >
          {showManualsShelf ? "Hide Manuals" : "Download Manuals"}
        </button>
      </div>

      {/* Small Download Manuals Shelf */}
      {showManualsShelf && (
        <div className="manuals-shelf">
          <div className="manuals-shelf-title">
            📄 Product Manuals (PDF):
          </div>
          <ul className="manuals-shelf-list">
            {AVAILABLE_MANUALS.map((m, idx) => (
              <li key={idx} className="manuals-shelf-item">
                <a
                  href={`/manuals/${m.file}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  download
                >
                  {m.name}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Chat Messages Area */}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-bubble-wrapper ${msg.sender}`}
          >
            <div
              className={`chat-bubble ${msg.sender === "user" ? "user-bubble" : "assistant-bubble"}`}
            >
              {msg.text}
            </div>

            {/* Source Attribution & PDF Download Link */}
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources-container">
                <div className="sources-heading">Sources & Documentation:</div>
                {msg.sources.map((src, sIdx) => (
                  <div key={sIdx} className="source-item">
                    <div>
                      <span className="source-title">{src.manual}</span>
                      <span className="source-section"> &bull; {src.section}</span>
                    </div>
                    <a
                      href={src.download_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="download-manual-link"
                      download
                    >
                      Download manual
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && <div className="chat-loading">Shop Assistant is thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Chips */}
      <div className="chat-suggestions">
        <button
          type="button"
          className="suggestion-chip"
          onClick={() => handleSend("How do I pair the wireless bluetooth headphones?")}
          disabled={loading}
        >
          Pairing headphones?
        </button>
        <button
          type="button"
          className="suggestion-chip"
          onClick={() => handleSend("Water bottle troubleshooting and leaks")}
          disabled={loading}
        >
          Water bottle troubleshooting
        </button>
        <button
          type="button"
          className="suggestion-chip"
          onClick={() => handleSend("What is the backpack warranty?")}
          disabled={loading}
        >
          Backpack warranty?
        </button>
        <button
          type="button"
          className="suggestion-chip"
          onClick={() => handleSend("What is in my cart?")}
          disabled={loading}
        >
          View cart
        </button>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about products, cart, orders, or manuals (how to use, troubleshooting, warranty)..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          autoFocus
        />
        <button type="submit" className="btn-send" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
