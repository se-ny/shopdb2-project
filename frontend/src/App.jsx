import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "./App.css";

// ============================================================
// 구매자
// ============================================================

// 구매자 상품 목록 / 상품 상세
import BuyerShop from "./pages/buyer/BuyerShop";

// ============================================================
// 판매자
// ============================================================

// 판매자 상품 / 옵션 / 이미지 / 재고 관리
import SellerProductList from "./pages/products/ProductList";
import ProductForm from "./pages/products/ProductForm";
import SellerOrderList from "./pages/orders/SellerOrderList";
import SellerProfile from "./pages/seller/SellerProfile";
import SellerDashboard from "./pages/seller/SellerDashboard";

// ============================================================
// 인증
// ============================================================

import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import RequireAdmin from "./components/RequireAdmin";

// ============================================================
// 관리자
// ============================================================

import AdminLayout from "./pages/admin/AdminLayout";
import Dashboard from "./pages/admin/Dashboard";
import OrgList from "./pages/admin/OrgList";
import OrderManagePage from "./pages/admin/OrderManagePage";
import UserList from "./pages/admin/UserList";
import PolicyList from "./pages/admin/PolicyList";
import PaymentRefundPage from "./pages/admin/PaymentRefundPage";
import AiRagPage from "./pages/admin/AiRagPage";
import FeedbackStats from "./pages/admin/FeedbackStats";
import SqlAgentPage from "./pages/admin/SqlAgentPage";
import AlertList from "./pages/admin/AlertList";
import ActionLogList from "./pages/admin/ActionLogList";
import ProductApprovalPage from "./pages/admin/ProductApprovalPage";
import CategoryList from "./pages/admin/CategoryList";
import AdminDataManager from "./pages/admin/AdminDataManager";


const API_BASE_URL = "http://127.0.0.1:8000";



function SellerPageNavigation({ onBack, backLabel }) {
  return (
    <div style={{ maxWidth: 1280, margin: "16px auto 0", padding: "0 24px" }}>
      <button type="button" onClick={onBack}>
        {backLabel}
      </button>
    </div>
  );
}

function HomePage() {
  const [backendStatus, setBackendStatus] = useState("확인 중");
  const [databaseStatus, setDatabaseStatus] = useState("확인 중");
  const [databaseInfo, setDatabaseInfo] = useState("");
  const [currentView, setCurrentView] = useState("home");
  const { auth, login, logout } = useAuth();
  const navigate = useNavigate();

  async function handleQuickLogin(loginId) {
    try {
      await login(loginId, loginId);
    } catch (error) {
      window.alert(
        error.message || `${loginId} 빠른 로그인에 실패했습니다.`
      );
    }
  }

  useEffect(() => {
    async function checkEnvironment() {
      try {
        const backendResponse = await fetch(`${API_BASE_URL}/api/health`);
        const backendData = await backendResponse.json();
        setBackendStatus(
          backendResponse.ok &&
          backendData.success &&
          backendData.status === "healthy"
            ? "정상"
            : "확인 필요"
        );

        const databaseResponse = await fetch(`${API_BASE_URL}/api/health/db`);
        const databaseData = await databaseResponse.json();

        if (
          databaseResponse.ok &&
          databaseData.success &&
          databaseData.status === "connected"
        ) {
          setDatabaseStatus("정상");
          setDatabaseInfo(
            `${databaseData.database} · 테이블 ${databaseData.table_count}개`
          );
        } else {
          setDatabaseStatus("확인 필요");
        }
      } catch {
        setBackendStatus("연결 실패");
        setDatabaseStatus("연결 실패");
      }
    }

    checkEnvironment();
  }, []);

  if (currentView === "buyer") {
    return (
      <>
        <div style={{ maxWidth: 1180, margin: "16px auto 0", padding: "0 24px" }}>
          <button type="button" onClick={() => setCurrentView("home")}>
            ← SHOPDB2 소개
          </button>
        </div>
        <BuyerShop />
      </>
    );
  }

  if (currentView === "seller") {
    return (
      <SellerDashboard
        onBack={() => setCurrentView("home")}
        onSelect={setCurrentView}
      />
    );
  }

  if (currentView === "seller-products") {
    return (
      <>
        <SellerPageNavigation
          onBack={() => setCurrentView("seller")}
          backLabel="← 판매자 운영"
        />
        <SellerProductList />
      </>
    );
  }

  if (currentView === "seller-orders") {
    return (
      <>
        <SellerPageNavigation
          onBack={() => setCurrentView("seller")}
          backLabel="← 판매자 운영"
        />
        <SellerOrderList />
      </>
    );
  }

  if (currentView === "seller-profile") {
    return (
      <>
        <SellerPageNavigation
          onBack={() => setCurrentView("seller")}
          backLabel="← 판매자 운영"
        />
        <SellerProfile />
      </>
    );
  }

  if (currentView === "seller-product-new") {
    return (
      <>
        <SellerPageNavigation
          onBack={() => setCurrentView("seller")}
          backLabel="← 판매자 운영"
        />
        <ProductForm />
      </>
    );
  }

  const isAdmin = Boolean(auth?.roles?.includes("ADMIN"));

  return (
    <main className="app">
      <header>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 18,
            alignItems: "flex-start",
            flexWrap: "wrap",
          }}
        >
          <div>
            <p className="project-label">SHOPDB2 TEAM PROJECT</p>
            <h1>SHOPDB2</h1>
            <p style={{ maxWidth: 720, lineHeight: 1.75 }}>
              구매자, 판매자, 관리자의 실제 쇼핑몰 업무 흐름을
              React · FastAPI · MySQL로 연결한 팀 프로젝트입니다.
              상품 탐색부터 주문·결제, 상품·재고 관리와 관리자 운영 기능까지
              역할별 흐름을 하나의 서비스에서 확인할 수 있습니다.
            </p>
          </div>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {auth ? (
              <>
                <span style={{ padding: "9px 4px" }}>
                  <strong>{auth.user_name}</strong> · {auth.roles.join(", ")}
                </span>
                <button type="button" onClick={logout}>로그아웃</button>
              </>
            ) : (
              <a href="/login">로그인</a>
            )}

            <button type="button" onClick={() => handleQuickLogin("admin01")}>
              관리자 로그인
            </button>
            <button type="button" onClick={() => handleQuickLogin("seller01")}>
              판매자 로그인
            </button>
            <button type="button" onClick={() => handleQuickLogin("buyer01")}>
              구매자 로그인
            </button>
          </div>
        </div>
      </header>

      <section
        className="status-card"
        style={{
          padding: "36px 32px",
          background: "#f8fbff",
          border: "1px solid #dbeafe",
        }}
      >
        <p className="project-label">SHOPDB2 TEAM PROJECT</p>
        <h2 style={{ fontSize: "clamp(28px, 4vw, 42px)", margin: "8px 0 14px" }}>
          SHOPDB2 쇼핑몰 팀 프로젝트
        </h2>
        <p style={{ maxWidth: 820, lineHeight: 1.8, color: "#475569", marginBottom: 0 }}>
          React · FastAPI · MySQL을 연동하여 구매자·판매자·관리자 기능을 구현했습니다.
          상단의 역할별 로그인 버튼으로 실제 계정에 로그인한 뒤
          각 역할의 기능과 접근 권한을 확인할 수 있습니다.
        </p>
      </section>

      <section className="role-section">
        <h2>SHOPDB2 주요 기능</h2>
        <div className="role-grid">
          <article>
            <p className="project-label">BUYER</p>
            <h3>구매자 쇼핑</h3>
            <p>상품 조회부터 옵션 선택, 장바구니, 주문과 결제까지 구매 흐름을 제공합니다.</p>
            <button type="button" onClick={() => setCurrentView("buyer")}>
              상품 둘러보기
            </button>
          </article>

          <article>
            <p className="project-label">SELLER</p>
            <h3>판매자 운영</h3>
            <p>상품·옵션·이미지·재고와 판매 관련 정보를 관리하는 업무 흐름입니다.</p>
            <button type="button" onClick={() => setCurrentView("seller")}>
              판매자 운영 들어가기
            </button>
          </article>

          <article>
            <p className="project-label">ADMIN</p>
            <h3>관리자 운영</h3>
            <p>회원·조직·상품 승인·주문·정책과 AI/RAG 등 운영 기능을 관리합니다.</p>
            {isAdmin && (
              <button type="button" onClick={() => navigate("/admin")}>
                관리자 운영 들어가기
              </button>
            )}
          </article>
        </div>
      </section>

      <section className="status-card">
        <h2>프로젝트 구성</h2>
        <p style={{ lineHeight: 1.75 }}>
          프론트엔드 React, 백엔드 FastAPI, 데이터베이스 MySQL을 연결하고
          역할과 업무 흐름에 따라 화면·API·데이터 처리를 분리했습니다.
        </p>
        <p style={{ marginTop: 14, color: "#64748b", fontSize: 13 }}>
          시스템 상태 · Backend {backendStatus} · Database {databaseStatus}
          {databaseInfo ? ` · ${databaseInfo}` : ""}
        </p>
      </section>

    </main>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>

          {/* 메인 / 구매자 / 판매자 */}
          <Route
            path="/"
            element={<HomePage />}
          />

          {/* 로그인 */}
          <Route
            path="/login"
            element={<LoginPage />}
          />


          {/* 관리자 */}
          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <AdminLayout />
              </RequireAdmin>
            }
          >
            <Route
              index
              element={<Dashboard />}
            />

            <Route
              path="dashboard"
              element={<Dashboard />}
            />

            <Route
              path="orgs"
              element={<OrgList />}
            />

            <Route
              path="orders"
              element={<OrderManagePage />}
            />

            <Route
              path="users"
              element={<UserList />}
            />

            <Route
              path="policies"
              element={<PolicyList />}
            />

            <Route
              path="payments"
              element={<PaymentRefundPage />}
            />

            <Route
              path="ai"
              element={<AiRagPage />}
            />

            <Route
              path="feedback"
              element={<FeedbackStats />}
            />

            <Route
              path="sql-agent"
              element={<SqlAgentPage />}
            />

            <Route
              path="alerts"
              element={<AlertList />}
            />

            <Route
              path="logs"
              element={<ActionLogList />}
            />

            <Route
              path="products"
              element={<ProductApprovalPage />}
            />

            <Route
              path="categories"
              element={<CategoryList />}
            />

            <Route
              path="data"
              element={<AdminDataManager />}
            />
          </Route>

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}


export default App;
