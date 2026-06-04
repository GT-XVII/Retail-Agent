const API_BASE = "http://localhost:8000";

export async function fetchProducts(query = "", limit = 50) {
  const params = new URLSearchParams();

  if (query) params.append("q", query);
  params.append("limit", limit);

  const response = await fetch(`${API_BASE}/products?${params}`);

  if (!response.ok) {
    throw new Error("Failed to fetch products");
  }

  return response.json();
}

export async function sendChatMessage(message) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error("Failed to send chat message");
  }

  return response.json();
}