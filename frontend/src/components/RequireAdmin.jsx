import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function RequireAdmin({ children }) {
  const { isAuthenticated, hasRole } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (!hasRole("ADMIN")) {
    return <p style={{ padding: 40 }}>접근 권한이 없습니다. (ADMIN 전용)</p>;
  }
  return children;
}

export default RequireAdmin;