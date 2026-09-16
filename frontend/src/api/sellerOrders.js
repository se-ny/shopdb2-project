const API_BASE_URL = "http://127.0.0.1:8000/api/seller";

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

  if (response.status === 204) {
    return null;
  }

  return response.json();
}


// 판매자 주문 목록 조회
export function getSellerOrders(
  sellerUserId,
) {
  const query = new URLSearchParams({
    seller_user_id: String(sellerUserId),
  });

  return request(
    `/orders?${query.toString()}`,
  );
}


// 판매자 주문 상세 조회
export function getSellerOrderDetail(
  orderId,
  sellerUserId,
) {
  const query = new URLSearchParams({
    seller_user_id: String(sellerUserId),
  });

  return request(
    `/orders/${orderId}?${query.toString()}`,
  );
}