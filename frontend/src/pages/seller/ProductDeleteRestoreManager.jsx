import { useState } from "react";
import {
  deleteProduct,
  getProducts,
  restoreProduct,
} from "../../api/products";

const STATUS_LABELS = {
  READY: "판매 준비",
  SALE: "판매 중",
  SOLD_OUT: "품절",
  STOPPED: "판매 중지",
  DELETED: "삭제 상태",
};

function formatPrice(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return `${number.toLocaleString("ko-KR")}원`;
}

export default function ProductDeleteRestoreManager({
  onBack,
}) {
  const [sellerUserId, setSellerUserId] =
    useState("");
  const [keyword, setKeyword] = useState("");
  const [products, setProducts] = useState([]);
  const [viewMode, setViewMode] =
    useState("ACTIVE");
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] =
    useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadProducts(
    nextMode = viewMode,
    nextKeyword = keyword,
  ) {
    const parsedSellerUserId = Number(
      sellerUserId,
    );

    if (
      !Number.isInteger(parsedSellerUserId) ||
      parsedSellerUserId < 1
    ) {
      setError(
        "판매자 사용자 ID를 1 이상의 정수로 입력해주세요.",
      );
      setProducts([]);
      return;
    }

    try {
      setLoading(true);
      setError("");
      setMessage("");

      const data = await getProducts({
        seller_user_id: parsedSellerUserId,
        keyword: nextKeyword.trim(),
        skip: 0,
        limit: 100,
      });

      const filtered = data.filter((product) =>
        nextMode === "DELETED"
          ? product.product_status === "DELETED"
          : product.product_status !== "DELETED",
      );

      setProducts(filtered);
    } catch (err) {
      setProducts([]);
      setError(
        err.message ||
          "상품 목록을 불러오지 못했습니다.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(event) {
    event.preventDefault();
    await loadProducts(viewMode, keyword);
  }

  async function handleModeChange(nextMode) {
    setViewMode(nextMode);
    await loadProducts(nextMode, keyword);
  }

  async function handleDelete(product) {
    const confirmed = window.confirm(
      `${product.product_name} 상품을 삭제 처리하시겠습니까?\n실제 DB 행은 삭제하지 않고 DELETED 상태로 변경됩니다.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingId(product.product_id);
      setError("");
      setMessage("");

      await deleteProduct(
        product.product_id,
        Number(sellerUserId),
      );

      setMessage(
        `${product.product_name} 상품이 삭제 상태로 변경되었습니다.`,
      );

      await loadProducts("ACTIVE", keyword);
    } catch (err) {
      setError(
        err.message ||
          "상품 삭제 처리에 실패했습니다.",
      );
    } finally {
      setProcessingId(null);
    }
  }

  async function handleRestore(product) {
    const confirmed = window.confirm(
      `${product.product_name} 상품을 복원하시겠습니까?\n복원 후 판매 준비(READY) 상태가 됩니다.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingId(product.product_id);
      setError("");
      setMessage("");

      await restoreProduct(
        product.product_id,
        Number(sellerUserId),
      );

      setMessage(
        `${product.product_name} 상품이 판매 준비(READY) 상태로 복원되었습니다.`,
      );

      await loadProducts("DELETED", keyword);
    } catch (err) {
      setError(
        err.message ||
          "상품 복원에 실패했습니다.",
      );
    } finally {
      setProcessingId(null);
    }
  }

  return (
    <section
      style={{
        width: "min(1120px, calc(100% - 48px))",
        margin: "0 auto",
        padding: "32px 0 72px",
      }}
    >
      <button
        type="button"
        onClick={onBack}
        style={{
          marginBottom: "24px",
          padding: "9px 14px",
          border: "1px solid #d7dce5",
          borderRadius: "7px",
          background: "#ffffff",
          cursor: "pointer",
        }}
      >
        ← 판매자 운영
      </button>

      <p
        style={{
          margin: "0 0 8px",
          fontSize: "12px",
          fontWeight: 700,
          letterSpacing: "0.08em",
        }}
      >
        SHOPDB2 SELLER
      </p>

      <h1
        style={{
          margin: "0 0 10px",
          fontSize: "32px",
          color: "#081f55",
        }}
      >
        상품 삭제 및 복원 관리
      </h1>

      <p
        style={{
          margin: "0 0 24px",
          color: "#566174",
          lineHeight: 1.7,
        }}
      >
        판매자의 등록 상품을 삭제 상태로 변경하거나,
        삭제된 상품을 판매 준비 상태로 복원합니다.
      </p>

      <form
        onSubmit={handleSearch}
        style={{
          display: "flex",
          gap: "10px",
          flexWrap: "wrap",
          marginBottom: "20px",
        }}
      >
        <input
          type="number"
          min="1"
          value={sellerUserId}
          onChange={(event) =>
            setSellerUserId(event.target.value)
          }
          placeholder="판매자 사용자 ID"
          style={{
            minWidth: "180px",
            padding: "10px 12px",
          }}
        />

        <input
          type="text"
          value={keyword}
          onChange={(event) =>
            setKeyword(event.target.value)
          }
          placeholder="상품명 또는 상품코드 검색"
          style={{
            minWidth: "260px",
            flex: "1 1 280px",
            padding: "10px 12px",
          }}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px 16px",
            cursor: "pointer",
          }}
        >
          {loading ? "조회 중..." : "조회"}
        </button>
      </form>

      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "22px",
          flexWrap: "wrap",
        }}
      >
        <button
          type="button"
          onClick={() =>
            handleModeChange("ACTIVE")
          }
          disabled={loading}
          style={{
            padding: "10px 15px",
            fontWeight:
              viewMode === "ACTIVE" ? 800 : 600,
            cursor: "pointer",
          }}
        >
          등록 상품
        </button>

        <button
          type="button"
          onClick={() =>
            handleModeChange("DELETED")
          }
          disabled={loading}
          style={{
            padding: "10px 15px",
            fontWeight:
              viewMode === "DELETED" ? 800 : 600,
            cursor: "pointer",
          }}
        >
          삭제 상품
        </button>
      </div>

      {error && (
        <p
          style={{
            padding: "12px 14px",
            border: "1px solid #f1b8b8",
            borderRadius: "8px",
          }}
        >
          {error}
        </p>
      )}

      {message && (
        <p
          style={{
            padding: "12px 14px",
            border: "1px solid #b8d7c1",
            borderRadius: "8px",
          }}
        >
          {message}
        </p>
      )}

      {!loading &&
        !error &&
        products.length === 0 && (
          <p
            style={{
              padding: "24px 0",
              color: "#64748b",
            }}
          >
            {viewMode === "DELETED"
              ? "삭제된 상품이 없습니다."
              : "조회된 등록 상품이 없습니다."}
          </p>
        )}

      <div
        style={{
          display: "grid",
          gap: "12px",
        }}
      >
        {products.map((product) => (
          <article
            key={product.product_id}
            style={{
              display: "grid",
              gridTemplateColumns:
                "minmax(0, 1fr) auto",
              gap: "18px",
              alignItems: "center",
              padding: "18px",
              border: "1px solid #dce3ed",
              borderRadius: "10px",
              background: "#ffffff",
            }}
          >
            <div>
              <strong
                style={{
                  display: "block",
                  marginBottom: "6px",
                  fontSize: "17px",
                }}
              >
                {product.product_name}
              </strong>

              <div
                style={{
                  display: "flex",
                  gap: "12px",
                  flexWrap: "wrap",
                  color: "#64748b",
                  fontSize: "14px",
                }}
              >
                <span>
                  상품번호 {product.product_id}
                </span>
                <span>
                  {product.product_code}
                </span>
                <span>
                  {STATUS_LABELS[
                    product.product_status
                  ] || product.product_status}
                </span>
                <span>
                  {formatPrice(
                    product.sale_price,
                  )}
                </span>
              </div>
            </div>

            {viewMode === "DELETED" ? (
              <button
                type="button"
                onClick={() =>
                  handleRestore(product)
                }
                disabled={
                  processingId ===
                  product.product_id
                }
                style={{
                  padding: "10px 15px",
                  cursor: "pointer",
                }}
              >
                {processingId ===
                product.product_id
                  ? "복원 중..."
                  : "상품 복원"}
              </button>
            ) : (
              <button
                type="button"
                onClick={() =>
                  handleDelete(product)
                }
                disabled={
                  processingId ===
                  product.product_id
                }
                style={{
                  padding: "10px 15px",
                  cursor: "pointer",
                }}
              >
                {processingId ===
                product.product_id
                  ? "삭제 중..."
                  : "상품 삭제"}
              </button>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
