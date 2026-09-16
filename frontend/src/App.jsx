import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useEffect, useState } from "react";
import ProductList from "./pages/products/ProductList";
import "./App.css";
import AdminLayout from "./pages/admin/AdminLayout";
import OrgList from "./pages/admin/OrgList";
import UserList from "./pages/admin/UserList";
import PolicyList from "./pages/admin/PolicyList";
import AiRagPage from "./pages/admin/AiRagPage";


const API_BASE_URL = "http://127.0.0.1:8000";

function HomePage() {
  const [backendStatus, setBackendStatus] = useState("확인 중");
  const [databaseStatus, setDatabaseStatus] = useState("확인 중");
  const [databaseInfo, setDatabaseInfo] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // 현재 화면
  // home   = 공통 개발환경 화면
  // seller = 판매자 상품관리 화면
  const [currentView, setCurrentView] = useState("home");

  useEffect(() => {
    async function checkDevelopmentEnvironment() {
      try {
        const backendResponse = await fetch(`${API_BASE_URL}/api/health`);
        if (!backendResponse.ok) throw new Error(`Backend HTTP ${backendResponse.status}`);

        const backendData = await backendResponse.json();
        setBackendStatus(backendData.success && backendData.status === "healthy" ? "정상 연결" : "응답 확인 필요");

        const databaseResponse = await fetch(`${API_BASE_URL}/api/health/db`);
        if (!databaseResponse.ok) throw new Error(`Database HTTP ${databaseResponse.status}`);

        const databaseData = await databaseResponse.json();
        if (databaseData.success && databaseData.status === "connected") {
          setDatabaseStatus("정상 연결");
          setDatabaseInfo(`${databaseData.database} · 테이블 ${databaseData.table_count}개`);
        } else {
          setDatabaseStatus("응답 확인 필요");
        }
      } catch (error) {
        setBackendStatus("연결 실패");
        setDatabaseStatus("연결 실패");
        setErrorMessage(error.message);
      }
    }
    checkDevelopmentEnvironment();
  }, []);

  if (currentView === "seller") {
    return (
      <>
        <div
          style={{
            maxWidth: "1280px",
            margin: "20px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={() => setCurrentView("home")}
            style={{
              padding: "10px 16px",
              border: "1px solid #dbe3ef",
              borderRadius: "8px",
              background: "#ffffff",
              cursor: "pointer",
            }}
          >
            ← 메인으로
          </button>
        </div>

        <ProductList />
      </>
    );
  }

  return (
    <main className="app">
      <header>
        <p className="project-label">
          React · FastAPI · MySQL
        </p>

        <h1>SHOPDB2</h1>

        <p>쇼핑몰 통합 서비스 공통 개발환경</p>
      </header>
      <section className="status-card">
        <h2>개발환경 연결 상태</h2>
        <div className="status-row">
          <strong>Frontend</strong>

          <span className="success">
            정상 실행
          </span>
        </div>
        <div className="status-row">
          <strong>Backend</strong>
          <span className={backendStatus === "정상 연결" ? "success" : "failure"}>{backendStatus}</span>
        </div>
        <div className="status-row">
          <strong>Database</strong>
          <span className={databaseStatus === "정상 연결" ? "success" : "failure"}>
            {databaseStatus}

            {databaseInfo &&
              ` · ${databaseInfo}`}
          </span>
        </div>
        {errorMessage && <p className="error-message">개발환경을 확인하세요: {errorMessage}</p>}
      </section>
      <section className="role-section">
        <h2>서비스 영역</h2>
        <div className="role-grid">
          <article>
            <h3>구매자</h3>

            <p>
              상품 조회, 주문, 결제, 환불, 문의
            </p>
          </article>
          <article>
            <h3>판매자</h3>

            <p>
              상품, 옵션, 이미지, 재고 관리
            </p>

            <button
              type="button"
              onClick={() =>
                setCurrentView("seller")
              }
              style={{
                marginTop: "16px",
                padding: "10px 14px",
                border: "0",
                borderRadius: "8px",
                background: "#1d4ed8",
                color: "#ffffff",
                cursor: "pointer",
              }}
            >
              상품 관리 열기
            </button>
          </article>
          <article>
            <h3>관리자</h3>

            <p>
              회원, 조직, 권한, 정책,
              AI/RAG 관리
            </p>
          </article>
        </div>
      </section>
    </main>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="orgs" element={<OrgList />} />
          <Route path="users" element={<UserList />} />
          <Route path="policies" element={<PolicyList />} />
          <Route path="ai" element={<AiRagPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;