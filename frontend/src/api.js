const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

function getAuthHeaders() {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = "An error occurred";
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        if (typeof errorData.detail === "string") {
          errorDetail = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorDetail = errorData.detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
        }
      }
    } catch {
      errorDetail = response.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

export async function registerUser({ name, email, password }) {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  return handleResponse(response);
}

export async function loginUser({ email, password }) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse(response);
}

export async function getProducts() {
  const response = await fetch(`${API_BASE_URL}/products`);
  return handleResponse(response);
}

export async function addProduct({ name, description, price, stock }) {
  const response = await fetch(`${API_BASE_URL}/products`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      name,
      description: description || null,
      price: parseFloat(price),
      stock: parseInt(stock, 10),
    }),
  });
  return handleResponse(response);
}

export async function getCart() {
  const response = await fetch(`${API_BASE_URL}/cart`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

export async function addToCart(productId, quantity = 1) {
  const response = await fetch(`${API_BASE_URL}/cart`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      product_id: productId,
      quantity,
    }),
  });
  return handleResponse(response);
}

export async function placeOrder({ full_name, phone, address, city, postal_code }) {
  const response = await fetch(`${API_BASE_URL}/orders`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      full_name,
      phone,
      address,
      city,
      postal_code,
    }),
  });
  return handleResponse(response);
}

export async function getMyOrders() {
  const response = await fetch(`${API_BASE_URL}/orders`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

export async function sendChatMessage(question) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ question }),
  });
  return handleResponse(response);
}
