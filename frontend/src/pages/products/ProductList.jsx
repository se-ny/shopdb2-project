import { useEffect, useState } from "react";
import { getProducts } from "../../api/products";
import ProductCard from "../../components/ProductCard";
import ProductDetail from "./ProductDetail";
import ProductForm from "./ProductForm";
import SellerOrderList from "../orders/SellerOrderList";
import "../../styles/product.css";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedProductId, setSelectedProductId] =
    useState(null);

  const [showCreateForm, setShowCreateForm] =
    useState(false);

  const [showSellerOrders, setShowSellerOrders] =
    useState(false);

  async function loadProducts(searchKeyword = "") {
    try {
      setLoading(true);
      setError("");

      const data = await getProducts({
        keyword: searchKeyword,
        product_status: "SALE",
        skip: 0,
        limit: 50,
      });

      setProducts(data);
    } catch (err) {
      setError(
        err.message ||
          "상품을 불러오지 못했습니다.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  function handleSubmit(event) {
    event.preventDefault();

    loadProducts(keyword.trim());
  }

  function handleProductClick(productId) {
    setSelectedProductId(productId);
    setShowCreateForm(false);
    setShowSellerOrders(false);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function handleBackToList() {
    setSelectedProductId(null);
    setShowCreateForm(false);
    setShowSellerOrders(false);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function handleOpenCreateForm() {
    setShowCreateForm(true);
    setSelectedProductId(null);
    setShowSellerOrders(false);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function handleOpenSellerOrders() {
    setShowSellerOrders(true);
    setSelectedProductId(null);
    setShowCreateForm(false);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  async function handleCreated() {
    setShowCreateForm(false);

    await loadProducts("");

    setKeyword("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  if (showSellerOrders) {
    return (
      <section>
        <div
          style={{
            maxWidth: "1200px",
            margin: "24px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={handleBackToList}
            style={{
              padding: "10px 16px",
              border: "1px solid #dddddd",
              borderRadius: "8px",
              background: "#ffffff",
              cursor: "pointer",
            }}
          >
            ← 상품 관리로
          </button>
        </div>

        <SellerOrderList />
      </section>
    );
  }

  if (showCreateForm) {
    return (
      <section>
        <div
          style={{
            maxWidth: "1280px",
            margin: "24px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={handleBackToList}
            style={{
              padding: "10px 16px",
              border: "1px solid #dddddd",
              borderRadius: "8px",
              background: "#ffffff",
              cursor: "pointer",
            }}
          >
            ← 상품 목록으로
          </button>
        </div>

        <ProductForm
          onCreated={handleCreated}
          onCancel={handleBackToList}
        />
      </section>
    );
  }

  if (selectedProductId !== null) {
    return (
      <section>
        <div
          style={{
            maxWidth: "1280px",
            margin: "24px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={handleBackToList}
            style={{
              padding: "10px 16px",
              border: "1px solid #dddddd",
              borderRadius: "8px",
              background: "#ffffff",
              cursor: "pointer",
            }}
          >
            ← 상품 목록으로
          </button>
        </div>

        <ProductDetail
          productId={selectedProductId}
        />
      </section>
    );
  }

  return (
    <section className="product-page">
      <div className="product-page__header">
        <div>
          <p className="product-page__eyebrow">
            SHOPDB2
          </p>

          <h1>상품 목록</h1>

          <p>
            상품·판매 담당 상품 관리
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: "12px",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <form
            className="product-search"
            onSubmit={handleSubmit}
          >
            <input
              type="text"
              value={keyword}
              onChange={(event) =>
                setKeyword(event.target.value)
              }
              placeholder="상품명 또는 상품코드 검색"
            />

            <button type="submit">
              검색
            </button>
          </form>

          <button
            type="button"
            onClick={handleOpenSellerOrders}
            style={{
              padding: "11px 18px",
              border: "1px solid #111111",
              borderRadius: "8px",
              background: "#ffffff",
              cursor: "pointer",
            }}
          >
            판매 주문 관리
          </button>

          <button
            type="button"
            onClick={handleOpenCreateForm}
            style={{
              padding: "11px 18px",
              border: "0",
              borderRadius: "8px",
              background: "#111111",
              color: "#ffffff",
              cursor: "pointer",
            }}
          >
            + 상품 등록
          </button>
        </div>
      </div>

      {loading && (
        <p className="product-state">
          상품을 불러오는 중입니다.
        </p>
      )}

      {error && (
        <p className="product-state product-state--error">
          {error}
        </p>
      )}

      {!loading &&
        !error &&
        products.length === 0 && (
          <p className="product-state">
            등록된 상품이 없습니다.
          </p>
        )}

      {!loading &&
        !error &&
        products.length > 0 && (
          <div className="product-grid">
            {products.map((product) => (
              <ProductCard
                key={product.product_id}
                product={product}
                onClick={() =>
                  handleProductClick(
                    product.product_id,
                  )
                }
              />
            ))}
          </div>
        )}
    </section>
  );
}