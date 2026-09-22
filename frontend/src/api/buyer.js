const API_BASE_URL = "http://127.0.0.1:8000";

function authHeader() {
  const saved = sessionStorage.getItem("auth");
  if (!saved) return {};

  try {
    const auth = JSON.parse(saved);
    return auth?.access_token
      ? { Authorization: `Bearer ${auth.access_token}` }
      : {};
  } catch {
    return {};
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeader(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // 기본 메시지 사용
    }

    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

export function getCart() {
  return request("/api/cart");
}

export function addCartItem(variantId, quantity) {
  return request("/api/cart/items", {
    method: "POST",
    body: JSON.stringify({
      variant_id: variantId,
      quantity,
    }),
  });
}

export function updateCartItem(cartItemId, quantity) {
  return request(`/api/cart/items/${cartItemId}`, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
}

export function deleteCartItem(cartItemId) {
  return request(`/api/cart/items/${cartItemId}`, {
    method: "DELETE",
  });
}

export function getOrders() {
  return request("/api/orders");
}

export function getOrder(orderId) {
  return request(`/api/orders/${orderId}`);
}

export function createOrder(payload) {
  return request("/api/orders", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getPaymentsByOrder(orderId) {
  return request(`/api/payments/order/${orderId}`);
}

export function createPayment(payload) {
  return request("/api/payments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createPaymentTransaction(paymentId, payload) {
  return request(`/api/payments/${paymentId}/transactions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getBuyerProducts() {
  return request("/api/products");
}

export function getBuyerProductDetail(productId) {
  return request(`/api/products/${productId}`);
}
