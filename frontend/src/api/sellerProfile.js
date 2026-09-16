const API_BASE_URL = "http://127.0.0.1:8000/api/seller/profile";

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;

    try {
      const data = await response.json();

      if (data.detail) {
        message = data.detail;
      }
    } catch {
      // JSON 응답이 아니면 기본 메시지 사용
    }

    throw new Error(message);
  }

  return response.json();
}

export function getSellerProfile(userId) {
  return request(`/${userId}`);
}

export function updateSellerProfile(
  userId,
  profile,
) {
  return request(`/${userId}`, {
    method: "PUT",
    body: JSON.stringify(profile),
  });
}