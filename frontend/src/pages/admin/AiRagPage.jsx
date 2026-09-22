import { useEffect, useState } from "react";
import {
  fetchProviders,
  fetchDocuments,
  indexDocument,
  queryRag,
  deactivateProvider,
  deleteDocument,
} from "../../api/admin";
import DocumentForm from "./DocumentForm";
import DocumentEditPanel from "./DocumentEditPanel";
import ProviderEditPanel from "./ProviderEditPanel";

function AiRagPage() {
  const [providers, setProviders] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [indexingId, setIndexingId] = useState(null);
  const [showDocForm, setShowDocForm] = useState(false);
  const [editingProviderId, setEditingProviderId] = useState(null);
  const [editingDocumentId, setEditingDocumentId] = useState(null);

  const [question, setQuestion] = useState("");
  const [providerCode, setProviderCode] = useState("OLLAMA");
  const [answer, setAnswer] = useState(null);
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryError, setQueryError] = useState("");

  function loadAll() {
    setLoading(true);
    Promise.all([fetchProviders(), fetchDocuments()])
      .then(([providerData, documentData]) => {
        setProviders(providerData);
        setDocuments(documentData);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function handleIndex(documentId) {
    setIndexingId(documentId);
    try {
      await indexDocument(documentId);
      loadAll();
    } catch (error) {
      alert(`인덱싱 실패: ${error.message}`);
    } finally {
      setIndexingId(null);
    }
  }

  async function handleDeleteDocument(doc) {
    if (!confirm(`"${doc.document_name}" 문서를 완전히 삭제하시겠습니까? (인덱싱 데이터도 함께 삭제됩니다)`)) return;
    try {
      await deleteDocument(doc.document_id);
      loadAll();
    } catch (error) {
      alert(`삭제 실패: ${error.message}`);
    }
  }

  async function handleDeactivateProvider(provider) {
    if (!confirm(`${provider.provider_code}를 비활성화하시겠습니까?`)) return;
    try {
      await deactivateProvider(provider.provider_id);
      loadAll();
    } catch (error) {
      alert(`비활성화 실패: ${error.message}`);
    }
  }

  async function handleQuerySubmit(event) {
    event.preventDefault();
    setQueryLoading(true);
    setQueryError("");
    setAnswer(null);
    try {
      const result = await queryRag({ question, provider_code: providerCode, top_k: 3 });
      setAnswer(result);
    } catch (error) {
      setQueryError(error.message);
    } finally {
      setQueryLoading(false);
    }
  }

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <h1>AI / RAG 관리</h1>

      <h2 className="policy-section-title">Provider 목록</h2>

      {editingProviderId && (
        <ProviderEditPanel
          provider={providers.find((p) => p.provider_id === editingProviderId)}
          onSaved={() => { setEditingProviderId(null); loadAll(); }}
          onCancel={() => setEditingProviderId(null)}
        />
      )}

      <table className="admin-table">
        <thead>
          <tr>
            <th>코드</th>
            <th>이름</th>
            <th>구분</th>
            <th>채팅 모델</th>
            <th>임베딩 모델</th>
            <th>상태</th>
            <th>동작</th>
          </tr>
        </thead>
        <tbody>
          {providers.map((provider) => (
            <tr key={provider.provider_id}>
              <td>{provider.provider_code}</td>
              <td>{provider.provider_name}</td>
              <td>{provider.provider_type}</td>
              <td>{provider.chat_model}</td>
              <td>{provider.embedding_model}</td>
              <td>{provider.active_yn === "Y" ? "활성" : "비활성"}</td>
              <td>
                <button onClick={() => setEditingProviderId(provider.provider_id)}>수정</button>
                {provider.active_yn === "Y" && (
                  <button onClick={() => handleDeactivateProvider(provider)}>비활성화</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="admin-page-header">
        <h2 className="policy-section-title">문서 목록 (인덱싱)</h2>
        {!showDocForm && <button onClick={() => setShowDocForm(true)}>+ 문서 등록</button>}
      </div>
      {showDocForm && (
        <DocumentForm
          providers={providers}
          onSaved={() => { setShowDocForm(false); loadAll(); }}
          onCancel={() => setShowDocForm(false)}
        />
      )}

      {editingDocumentId && (
        <DocumentEditPanel
          document={documents.find((d) => d.document_id === editingDocumentId)}
          onSaved={() => { setEditingDocumentId(null); loadAll(); }}
          onCancel={() => setEditingDocumentId(null)}
        />
      )}

      <table className="admin-table">
        <thead>
          <tr>
            <th>문서명</th>
            <th>종류</th>
            <th>상태</th>
            <th>동작</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.document_id}>
              <td>{doc.document_name}</td>
              <td>{doc.document_type}</td>
              <td>{doc.document_status}</td>
              <td>
                <button
                  onClick={() => handleIndex(doc.document_id)}
                  disabled={indexingId === doc.document_id}
                >
                  {indexingId === doc.document_id ? "인덱싱 중..." : "인덱싱 실행"}
                </button>
                <button onClick={() => setEditingDocumentId(doc.document_id)}>수정</button>
                <button onClick={() => handleDeleteDocument(doc)}>삭제</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="policy-section-title">질의응답 테스트</h2>
      <form onSubmit={handleQuerySubmit} className="rag-query-form">
        <select value={providerCode} onChange={(e) => setProviderCode(e.target.value)}>
          <option value="OLLAMA">OLLAMA</option>
          <option value="OPENAI">OPENAI</option>
          <option value="GEMINI">GEMINI</option>
        </select>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="질문을 입력하세요 (예: 환불 가능한 기간이 며칠이야?)"
        />
        <button type="submit" disabled={queryLoading || !question}>
          {queryLoading ? "답변 생성 중..." : "질문하기"}
        </button>
      </form>

      {queryError && <p className="error-message">{queryError}</p>}

      {answer && (
        <div className="rag-answer-box">
          <p className="rag-answer-text">{answer.answer}</p>
          <p className="rag-answer-meta">
            참고 청크 {answer.retrieved_chunks.length}건 · 응답시간 {answer.response_time_ms}ms
          </p>
        </div>
      )}
    </div>
  );
}

export default AiRagPage;