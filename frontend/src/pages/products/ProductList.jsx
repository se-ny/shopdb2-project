import { useEffect, useState } from "react";
import { getProducts } from "../../api/products";
import ProductCard from "../../components/ProductCard";
import ProductDetail from "./ProductDetail";
import ProductForm from "./ProductForm";
import SellerOrderList from "../orders/SellerOrderList";
import SellerProfile from "../seller/SellerProfile";
import "../../styles/product.css";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [currentView, setCurrentView] =
    useState("list");

  const [selectedProductId, setSelectedProductId] =
    useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      try {
        await Promise.resolve();

        const data = await getProducts({
          keyword: "",
          skip: 0,
          limit: 50,
        });

        if (!cancelled) {
          setProducts(
            data.filter(
              (product) =>
                product.product_status !== "DELETED",
            ),
          );
          setError("");
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "상품을 불러오지 못했습니다.",
          );
          setLoading(false);
        }
      }
    }

    loadProducts();

    return () => {
      cancelled = true;
    };
  }, []);

  async function searchProducts(searchKeyword) {
    try {
      setLoading(true);
      setError("");

      const data = await getProducts({
        keyword: searchKeyword,
        skip: 0,
        limit: 50,
      });

      setProducts(
        data.filter(
          (product) =>
            product.product_status !== "DELETED",
        ),
      );
    } catch (err) {
      setError(
        err.message ||
          "상품을 불러오지 못했습니다.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    searchProducts(keyword);
  }

  function handleProductClick(product) {
    setSelectedProductId(product.product_id);
    setCurrentView("detail");
  }

  function handleBackToList() {
    setSelectedProductId(null);
    setCurrentView("list");
    searchProducts(keyword);
  }

  if (
    currentView === "detail" &&
    selectedProductId
  ) {
    return (
      <>
        <div
          style={{
            maxWidth: 1280,
            margin: "16px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={handleBackToList}
          >
            ← 상품 목록으로
          </button>
        </div>

        <ProductDetail
          productId={selectedProductId}
          onBack={handleBackToList}
        />
      </>
    );
  }

  if (currentView === "create") {
    return (
      <>
        <div
          style={{
            maxWidth: 1280,
            margin: "16px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={handleBackToList}
          >
            ← 상품 목록으로
          </button>
        </div>

        <ProductForm onBack={handleBackToList} />
      </>
    );
  }

  if (currentView === "orders") {
    return (
      <>
        <div
          style={{
            maxWidth: 1280,
            margin: "16px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={handleBackToList}
          >
            ← 상품 관리로
          </button>
        </div>

        <SellerOrderList
          onBack={handleBackToList}
        />
      </>
    );
  }

  if (currentView === "profile") {
    return (
      <>
        <div
          style={{
            maxWidth: 1280,
            margin: "16px auto 0",
            padding: "0 24px",
          }}
        >
          <button
            type="button"
            onClick={handleBackToList}
          >
            ← 상품 관리로
          </button>
        </div>

        <SellerProfile
          onBack={handleBackToList}
        />
      </>
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
          <p>상품·판매 담당 상품 관리</p>
        </div>

        <div
          style={{
            display: "flex",
            gap: "8px",
            alignItems: "center",
            flexWrap: "wrap",
            justifyContent: "flex-end",
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

            <button type="submit">검색</button>
          </form>

          <button
            type="button"
            onClick={() =>
              setCurrentView("orders")
            }
          >
            판매 주문 관리
          </button>

          <button
            type="button"
            onClick={() =>
              setCurrentView("profile")
            }
          >
            판매자 정보 관리
          </button>

          <button
            type="button"
            onClick={() =>
              setCurrentView("create")
            }
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
                  handleProductClick(product)
                }
              />
            ))}
          </div>
        )}
    </section>
  );
}
