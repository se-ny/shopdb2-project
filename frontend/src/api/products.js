const API_BASE_URL = "http://127.0.0.1:8000/api";

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export function getProducts(params = {}) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, value);
    }
  });

  const suffix = query.toString() ? `?${query.toString()}` : "";

  return request(`/products${suffix}`);
}

export function getProduct(productId) {
  return request(`/products/${productId}`);
}

export function createProduct(product) {
  return request("/products", {
    method: "POST",
    body: JSON.stringify(product),
  });
}

export function updateProduct(productId, product) {
  return request(`/products/${productId}`, {
    method: "PUT",
    body: JSON.stringify(product),
  });
}

export function deleteProduct(productId) {
  return request(`/products/${productId}`, {
    method: "DELETE",
  });
}

export function getProductVariants(productId) {
  return request(`/products/${productId}/variants`);
}

export function createProductVariant(productId, variant) {
  return request(`/products/${productId}/variants`, {
    method: "POST",
    body: JSON.stringify(variant),
  });
}

export function updateProductVariant(productId, variantId, variant) {
  return request(`/products/${productId}/variants/${variantId}`, {
    method: "PUT",
    body: JSON.stringify(variant),
  });
}

export function deleteProductVariant(productId, variantId) {
  return request(`/products/${productId}/variants/${variantId}`, {
    method: "DELETE",
  });
}

export function getProductInventory(productId) {
  return request(`/products/${productId}/inventory`);
}

export function updateProductInventory(
  productId,
  inventoryId,
  inventory,
) {
  return request(
    `/products/${productId}/inventory/${inventoryId}`,
    {
      method: "PUT",
      body: JSON.stringify(inventory),
    },
  );
}