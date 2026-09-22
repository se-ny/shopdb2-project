import { useEffect, useState } from "react";
import { fetchAdminProducts, approveProduct, rejectProduct } from "../../api/admin";

const STATUS_OPTIONS = ["READY", "SALE", "SOLD_OUT", "STOPPED", "DELETED"];
const PAGE_SIZE = 20;

function ProductApprovalPage() {
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [statusFilter, setStatusFilter] = useState("READY");
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  function loadProducts() {
    setLoading(true);
    fetchAdminProducts({
      product_status: statusFilter,
      skip: page * PAGE_SIZE,
      limit: PAGE_SIZE,
    })
      .then((data) => {
        setProducts(data.items);
        setTotal(data.total);
      })
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, page]);

  async function handleApprove(product) {
    if (!confirm(`"${product.product_name}"을(를) 승인하시겠습니까? (판매 상태로 전환)`)) return;
    try {
      await approveProduct(product.product_id);
      loadProducts();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  async function handleReject(product) {
    if (!confirm(`"${product.product_name}"을(를) 반려하시겠습니까?`)) return;
    try {
      await rejectProduct(product.product_id);
      loadProducts();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div>
      <div className="admin-page-header">
        <h1>상품승인관리</h1>
      </div>

      <div style={{ marginBottom: 16 }}>
        <select
          value={statusFilter}
          onChange={(e) => { setPage(0); setStatusFilter(e.target.value); }}
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      {loading ? (
        <p>불러오는 중...</p>
      ) : (
        <>
          <table className="admin-table">
            <thead>
              <tr>
                <th>상품코드</th>
                <th>상품명</th>
                <th>판매자</th>
                <th>정상가</th>
                <th>판매가</th>
                <th>상태</th>
                <th>등록일</th>
                <th>동작</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.product_id}>
                  <td>{p.product_code}</td>
                  <td>{p.product_name}</td>
                  <td>{p.seller_name}</td>
                  <td>{p.regular_price}</td>
                  <td>{p.sale_price}</td>
                  <td>{p.product_status}</td>
                  <td>{new Date(p.created_at).toLocaleDateString()}</td>
                  <td>
                    {p.product_status === "READY" && (
                      <>
                        <button onClick={() => handleApprove(p)}>승인</button>
                        <button onClick={() => handleReject(p)}>반려</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", color: "#9ca3af" }}>
                    표시할 상품이 없습니다.
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
            <button disabled={page === 0} onClick={() => setPage((p) => p - 1)}>이전</button>
            <span>{page + 1} / {totalPages} (총 {total}건)</span>
            <button disabled={page + 1 >= totalPages} onClick={() => setPage((p) => p + 1)}>다음</button>
          </div>
        </>
      )}
    </div>
  );
}

export default ProductApprovalPage;