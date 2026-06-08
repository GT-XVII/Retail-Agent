const API_BASE = "http://localhost:8000";

class ApiError extends Error {
  constructor(message, { code = "api_error", details = {}, status = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.details = details;
    this.status = status;
  }
}

async function parseErrorResponse(response, fallbackMessage) {
  let payload;

  try {
    payload = await response.json();
  } catch {
    throw new ApiError(fallbackMessage, {
      code: "http_error",
      status: response.status,
    });
  }

  if (payload?.error) {
    throw new ApiError(payload.error.message || fallbackMessage, {
      code: payload.error.code,
      details: payload.error.details,
      status: response.status,
    });
  }

  if (payload?.detail) {
    throw new ApiError(formatDetail(payload.detail), {
      code: "request_error",
      details: payload.detail,
      status: response.status,
    });
  }

  throw new ApiError(fallbackMessage, {
    code: "http_error",
    details: payload,
    status: response.status,
  });
}

function formatDetail(detail) {
  if (typeof detail === "string") return detail;

  return JSON.stringify(detail);
}

export async function fetchProducts(query = "", limit = 50) {
  const params = new URLSearchParams();

  if (query) params.append("q", query);
  params.append("limit", limit);

  const response = await fetch(`${API_BASE}/products?${params}`);

  if (!response.ok) {
    await parseErrorResponse(response, "Failed to fetch products");
  }

  return response.json();
}

export async function sendChatMessage(message) {
  let response;

  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
  } catch (error) {
    throw new ApiError("Unable to reach the backend chat service.", {
      code: "network_error",
      details: {
        message: error.message,
      },
    });
  }

  if (!response.ok) {
    await parseErrorResponse(response, "Failed to send chat message");
  }

  return response.json();
}

export async function fetchCart() {
  const response = await fetch(`${API_BASE}/cart`);

  if (!response.ok) {
    await parseErrorResponse(response, "Failed to fetch cart");
  }

  return response.json();
}

export async function addToCart(productId, quantity = 1) {
  const response = await fetch(`${API_BASE}/cart/add`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      product_id: productId,
      quantity,
    }),
  });

  if (!response.ok) {
    await parseErrorResponse(response, "Failed to add item to cart");
  }

  return response.json();
}

export async function removeFromCart(productId) {
  const response = await fetch(`${API_BASE}/cart/remove`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      product_id: productId,
    }),
  });

  if (!response.ok) {
    await parseErrorResponse(response, "Failed to remove item from cart");
  }

  return response.json();
}
