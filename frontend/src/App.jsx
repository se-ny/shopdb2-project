import { useEffect, useState } from "react";
import "./App.css";
import ProductList from "./components/ProductList";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [backendStatus, setBackendStatus] = useState("확인 중");
  const [databaseStatus, setDatabaseStatus] = useState("확인 중");
  const [databaseInfo, setDatabaseInfo] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function checkDevelopmentEnvironment() {
      try {
        const backendResponse = await fetch(
          `${API_BASE_URL}/api/health`
        );

        if (!backendResponse.ok) {
          throw new Error(`Backend HTTP ${backendResponse.status}`);
        }

        const backendData = await backendResponse.json();

        if (backendData.success && backendData.status === "healthy") {
          setBackendStatus("정상 연결");
        } else {
          setBackendStatus("응답 확인 필요");
        }

        const databaseResponse = await fetch(
          `${API_BASE_URL}/api/health/db`
        );

        if (!databaseResponse.ok) {
          throw new Error(`Database HTTP ${databaseResponse.status}`);
        }

        const databaseData = await databaseResponse.json();

        if (
          databaseData.success &&
          databaseData.status === "connected"
        ) {
          setDatabaseStatus("정상 연결");
          setDatabaseInfo(
            `${databaseData.database} · 테이블 ${databaseData.table_count}개`
          );
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

  return (
    <main className="app">
      <header>
        <p className="project-label">React · FastAPI · MySQL</p>
        <h1>SHOPDB2</h1>
        <p>쇼핑몰 통합 서비스 공통 개발환경</p>
      </header>

      <section className="status-card">
        <h2>개발환경 연결 상태</h2>

        <div className="status-row">
          <strong>Frontend</strong>
          <span className="success">정상 실행</span>
        </div>

        <div className="status-row">
          <strong>Backend</strong>
          <span
            className={
              backendStatus === "정상 연결"
                ? "success"
                : "failure"
            }
          >
            {backendStatus}
          </span>
        </div>

        <div className="status-row">
          <strong>Database</strong>

          <span
            className={
              databaseStatus === "정상 연결"
                ? "success"
                : "failure"
            }
          >
            {databaseStatus}
            {databaseInfo && ` · ${databaseInfo}`}
          </span>
        </div>

        {errorMessage && (
          <p className="error-message">
            개발환경을 확인하세요: {errorMessage}
          </p>
        )}
      </section>

      <section className="role-section">
        <h2>서비스 영역</h2>

        <div className="role-grid">
          <article>
            <h3>구매자</h3>
            <p>상품 조회, 주문, 결제, 환불, 문의</p>
          </article>

          <article>
            <h3>판매자</h3>
            <p>상품, 옵션, 이미지, 재고 관리</p>
          </article>

          <article>
            <h3>관리자</h3>
            <p>회원, 조직, 권한, 정책, AI/RAG 관리</p>
          </article>
        </div>
           </section>

      <ProductList />
    </main>
  );
}