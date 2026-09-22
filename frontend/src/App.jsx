import { BrowserRouter, Routes, Route } from "react-router-dom";
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


const API_BASE_URL = "http://127.0.0.1:8000";


function HomePage() {
  const [backendStatus, setBackendStatus] = useState("확인 중");
  const [databaseStatus, setDatabaseStatus] = useState("확인 중");
  const [databaseInfo, setDatabaseInfo] = useState("");
  const [showTeacherTest, setShowTeacherTest] = useState(false);
  const [currentView, setCurrentView] = useState("home");
  const { auth, logout } = useAuth();

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
      <>
        <div style={{ maxWidth: 1280, margin: "16px auto 0", padding: "0 24px" }}>
          <button type="button" onClick={() => setCurrentView("home")}>
            ← SHOPDB2 소개
          </button>
        </div>
        <SellerProductList />
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

            <button
              type="button"
              onClick={() => setShowTeacherTest(true)}
              style={{
                padding: "10px 16px",
                border: "0",
                borderRadius: 8,
                background: "#1d4ed8",
                color: "#fff",
                fontWeight: 800,
                cursor: "pointer",
              }}
            >
              선생님 테스트
            </button>
          </div>
        </div>
      </header>

      <section
        className="status-card"
        style={{
          padding: "42px 32px",
          background: "#f8fbff",
          border: "1px solid #dbeafe",
        }}
      >
        <p className="project-label">ROLE BASED COMMERCE</p>
        <h2 style={{ fontSize: "clamp(28px, 4vw, 46px)", margin: "8px 0 14px" }}>
          역할별 업무 흐름을 연결한 쇼핑몰
        </h2>
        <p style={{ maxWidth: 760, lineHeight: 1.8, color: "#475569" }}>
          구매자는 상품을 탐색하고 장바구니·주문·결제를 진행합니다.
          판매자는 상품과 옵션·이미지·재고를 관리하고,
          관리자는 회원·조직·주문·정책·상품 승인과 운영 기능을 관리합니다.
        </p>
        <div style={{ display: "flex", gap: 10, marginTop: 22, flexWrap: "wrap" }}>
          <button
            type="button"
            onClick={() => setCurrentView("buyer")}
            style={{
              padding: "12px 18px",
              border: 0,
              borderRadius: 8,
              background: "#111827",
              color: "#fff",
              fontWeight: 800,
              cursor: "pointer",
            }}
          >
            상품 둘러보기
          </button>
          <button
            type="button"
            onClick={() => setShowTeacherTest(true)}
            style={{
              padding: "12px 18px",
              border: "1px solid #cbd5e1",
              borderRadius: 8,
              background: "#fff",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            구현 기능 테스트
          </button>
        </div>
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
          </article>

          <article>
            <p className="project-label">ADMIN</p>
            <h3>관리자 운영</h3>
            <p>회원·조직·상품 승인·주문·정책과 AI/RAG 등 운영 기능을 관리합니다.</p>
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

      {showTeacherTest && (
        <div
          role="presentation"
          onClick={() => setShowTeacherTest(false)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            display: "grid",
            placeItems: "center",
            padding: 20,
            background: "rgba(15, 23, 42, 0.58)",
          }}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby="teacher-test-title"
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(680px, 100%)",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: 28,
              borderRadius: 16,
              background: "#fff",
              boxShadow: "0 24px 70px rgba(15, 23, 42, 0.24)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 12,
                alignItems: "flex-start",
              }}
            >
              <div>
                <p className="project-label">TEACHER TEST</p>
                <h2 id="teacher-test-title" style={{ marginTop: 4 }}>
                  SHOPDB2 기능 테스트
                </h2>
                <p style={{ lineHeight: 1.7, color: "#64748b" }}>
                  역할별 구현 기능을 빠르게 확인할 수 있습니다.
                  테스트 계정의 비밀번호는 화면이나 소스에 공개하지 않습니다.
                </p>
              </div>
              <button type="button" onClick={() => setShowTeacherTest(false)}>
                닫기
              </button>
            </div>

            <div style={{ display: "grid", gap: 12, marginTop: 22 }}>
              <article className="status-card" style={{ margin: 0 }}>
                <h3>관리자 기능 테스트</h3>
                <p>회원 · 조직 · 상품 승인 · 주문 · 결제/환불 · 정책 · AI/RAG · 관리 로그</p>
                <a href={isAdmin ? "/admin" : "/login"}>
                  {isAdmin ? "관리자 화면 열기" : "관리자 로그인"}
                </a>
              </article>

              <article className="status-card" style={{ margin: 0 }}>
                <h3>구매자 기능 테스트</h3>
                <p>상품 조회 · 옵션/수량 · 장바구니 · 주문 · 결제 · 주문내역</p>
                <button
                  type="button"
                  onClick={() => {
                    setShowTeacherTest(false);
                    setCurrentView("buyer");
                  }}
                >
                  구매자 화면 열기
                </button>
              </article>

              <article className="status-card" style={{ margin: 0 }}>
                <h3>판매자 기능 테스트</h3>
                <p>상품 · 옵션 · 이미지 · 재고 · 판매 관련 관리 기능</p>
                <button
                  type="button"
                  onClick={() => {
                    setShowTeacherTest(false);
                    setCurrentView("seller");
                  }}
                >
                  판매자 화면 열기
                </button>
              </article>
            </div>
          </section>
        </div>
      )}
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
          </Route>

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}


export default App;