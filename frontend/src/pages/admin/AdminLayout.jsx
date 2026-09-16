import { NavLink, Outlet } from "react-router-dom";
import "../../styles/admin.css";

const MENU_ITEMS = [
  { to: "/admin/orgs", label: "조직관리" },
  { to: "/admin/users", label: "회원/권한" },
  { to: "/admin/policies", label: "정책관리" },
  { to: "/admin/ai", label: "AI / RAG" },
];

function AdminLayout() {
  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <h2>관리자</h2>
        <nav>
          {MENU_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
}

export default AdminLayout;