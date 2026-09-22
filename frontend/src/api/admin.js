const API_BASE_URL = "http://127.0.0.1:8000";

function authHeader() {
  const saved = sessionStorage.getItem("auth");
  if (!saved) return {};
  const { access_token } = JSON.parse(saved);
  return { Authorization: `Bearer ${access_token}` };
}

async function handleResponse(response) {
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// ---- 조직관리 ----
export async function fetchOrgs() {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function createOrg(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function deactivateOrg(orgId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs/${orgId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function updateOrg(orgId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs/${orgId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function activateOrg(orgId) {
  return updateOrg(orgId, { active_yn: "Y" });
}

// ---- 회원/권한 ----
export async function fetchUsers() {
  const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function fetchRoles() {
  const response = await fetch(`${API_BASE_URL}/api/admin/roles`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function updateUser(userId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function createUser(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function withdrawUser(userId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function assignRole(userId, roleId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/roles`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify({ role_id: roleId }),
  });
  return handleResponse(response);
}

export async function removeRole(userId, roleId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/roles/${roleId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  return handleResponse(response);
}

// ---- 정책 ----
export async function fetchCompanyPolicies() {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/company`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function fetchRefundPolicies() {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/refund`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function createCompanyPolicy(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/company`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function updateCompanyPolicy(policyId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/company/${policyId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function expireCompanyPolicy(policyId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/company/${policyId}/expire`, {
    method: "PATCH",
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function createRefundPolicy(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/refund`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function updateRefundPolicy(refundPolicyId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/refund/${refundPolicyId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function expireRefundPolicy(refundPolicyId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/refund/${refundPolicyId}/expire`, {
    method: "PATCH",
    headers: authHeader(),
  });
  return handleResponse(response);
}

// ---- AI / RAG ----
export async function fetchProviders() {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/providers`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function updateProvider(providerId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/providers/${providerId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function deactivateProvider(providerId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/providers/${providerId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function createDocument(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function indexDocument(documentId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents/${documentId}/index`, {
    method: "POST",
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function updateDocument(documentId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents/${documentId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function deleteDocument(documentId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents/${documentId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `HTTP ${response.status}`);
  }
  // 204 No Content라 body가 없음
  return true;
}

export async function queryRag(payload) {
  const response = await fetch(`${API_BASE_URL}/api/ai/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

// ---- 관리자 활동 로그 ----
export async function fetchActionLogs(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, value]) => value !== undefined && value !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/admin/action-logs${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

// ---- 결제/환불관리 ----
export async function fetchAdminPayments(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/admin/payments${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function fetchAdminRefunds(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/admin/refunds${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function forceCancelPayment(paymentId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/payments/${paymentId}/force-cancel`, {
    method: "PATCH",
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function approveRefund(refundRequestId, approvedAmount) {
  const response = await fetch(`${API_BASE_URL}/api/admin/refunds/${refundRequestId}/approve`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(approvedAmount ? { approved_amount: approvedAmount } : {}),
  });
  return handleResponse(response);
}

export async function rejectRefund(refundRequestId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/refunds/${refundRequestId}/reject`, {
    method: "PATCH",
    headers: authHeader(),
  });
  return handleResponse(response);
}
// ---- 시스템 알림 ----
export async function fetchAlerts(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/admin/alerts${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function resolveAlert(alertId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/alerts/${alertId}/resolve`, {
    method: "PATCH",
    headers: authHeader(),
  });
  return handleResponse(response);
}
// ---- AI 응답 피드백 ----
export async function submitFeedback(payload) {
  const response = await fetch(`${API_BASE_URL}/api/ai/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function fetchFeedbackList(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/ai/feedback${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function fetchFeedbackStats() {
  const response = await fetch(`${API_BASE_URL}/api/ai/feedback/stats`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}
// ---- 자연어 SQL 에이전트 ----
export async function querySqlAgent(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/sql-agent/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function fetchSqlAgentLogs(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/admin/sql-agent/logs${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}
// ---- 주문관리 ----
export async function fetchAdminOrders(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/admin/orders${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function fetchAdminOrderDetail(orderId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/orders/${orderId}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}
// ---- 대시보드 ----
export async function fetchDashboardSummary() {
  const response = await fetch(`${API_BASE_URL}/api/admin/dashboard/summary`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}
// ---- 상품승인관리 ----
export async function fetchAdminProducts(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
    )
  ).toString();
  const response = await fetch(`${API_BASE_URL}/api/admin/products${query ? `?${query}` : ""}`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function approveProduct(productId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/products/${productId}/approve`, {
    method: "PATCH",
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function rejectProduct(productId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/products/${productId}/reject`, {
    method: "PATCH",
    headers: authHeader(),
  });
  return handleResponse(response);
}
// ---- 카테고리관리 ----
export async function fetchCategories() {
  const response = await fetch(`${API_BASE_URL}/api/admin/categories`, {
    headers: authHeader(),
  });
  return handleResponse(response);
}

export async function createCategory(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/categories`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function updateCategory(categoryId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/categories/${categoryId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function deactivateCategory(categoryId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/categories/${categoryId}`, {
    method: "DELETE",
    headers: authHeader(),
  });
  return handleResponse(response);
}