const API_BASE_URL = "http://127.0.0.1:8000";

async function handleResponse(response) {
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// ---- 조직관리 ----
export async function fetchOrgs() {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs`);
  return handleResponse(response);
}

export async function createOrg(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function deactivateOrg(orgId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs/${orgId}`, {
    method: "DELETE",
  });
  return handleResponse(response);
}

export async function updateOrg(orgId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/orgs/${orgId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

// ---- 회원/권한 ----
export async function fetchUsers() {
  const response = await fetch(`${API_BASE_URL}/api/admin/users`);
  return handleResponse(response);
}

export async function fetchRoles() {
  const response = await fetch(`${API_BASE_URL}/api/admin/roles`);
  return handleResponse(response);
}

export async function updateUser(userId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function assignRole(userId, roleId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/roles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role_id: roleId }),
  });
  return handleResponse(response);
}

export async function removeRole(userId, roleId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/roles/${roleId}`, {
    method: "DELETE",
  });
  return handleResponse(response);
}

// ---- 정책 ----
export async function fetchCompanyPolicies() {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/company`);
  return handleResponse(response);
}

export async function fetchRefundPolicies() {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/refund`);
  return handleResponse(response);
}

export async function createCompanyPolicy(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/company`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function expireCompanyPolicy(policyId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/company/${policyId}/expire`, {
    method: "PATCH",
  });
  return handleResponse(response);
}

export async function createRefundPolicy(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/refund`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function expireRefundPolicy(refundPolicyId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/policies/refund/${refundPolicyId}/expire`, {
    method: "PATCH",
  });
  return handleResponse(response);
}

// ---- AI / RAG ----
export async function fetchProviders() {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/providers`);
  return handleResponse(response);
}

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents`);
  return handleResponse(response);
}

export async function createDocument(payload) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function indexDocument(documentId) {
  const response = await fetch(`${API_BASE_URL}/api/admin/ai/documents/${documentId}/index`, {
    method: "POST",
  });
  return handleResponse(response);
}

export async function queryRag(payload) {
  const response = await fetch(`${API_BASE_URL}/api/ai/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}