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