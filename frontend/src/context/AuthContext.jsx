import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);
const API_BASE_URL = "http://127.0.0.1:8000";

// 예전에 localStorage에 남아있던 로그인 정보 정리
localStorage.removeItem("auth");

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const saved = sessionStorage.getItem("auth");
    return saved ? JSON.parse(saved) : null;
  });

  async function login(loginId, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login_id: loginId, password }),
    });
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || "로그인에 실패했습니다.");
    }
    const data = await response.json();
    setAuth(data);
    sessionStorage.setItem("auth", JSON.stringify(data));
    return data;
  }

  function logout() {
    setAuth(null);
    sessionStorage.removeItem("auth");
  }

  function hasRole(role) {
    return !!auth?.roles?.includes(role);
  }

  return (
    <AuthContext.Provider value={{ auth, login, logout, hasRole, isAuthenticated: !!auth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}