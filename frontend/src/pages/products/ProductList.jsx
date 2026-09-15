import { useEffect, useState } from "react";
import { getProducts } from "../../api/products";
import ProductCard from "../../components/ProductCard";
import "../../styles/product.css";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      try {
        await Promise.resolve();

        const data = await getProducts({
          keyword: "",
          product_status: "SALE",
          skip: 0,
          limit: 50,
        });

        if (!cancelled) {
          setProducts(data);
          setError("");
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || "상품을 불러오지 못했습니다.",
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
        product_status: "SALE",
        skip: 0,
        limit: 50,
      });

      setProducts(data);
    } catch (err) {
      setError(
        err.message || "상품을 불러오지 못했습니다.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    searchProducts(keyword);
  }

  return (
    <section className="product-page">
      <div className="product-page__header">
        <div>
          <p className="product-page__eyebrow">SHOPDB2</p>
          <h1>상품 목록</h1>
          <p>상품·판매 담당 상품 관리</p>
        </div>

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

      {!loading && !error && products.length === 0 && (
        <p className="product-state">
          등록된 상품이 없습니다.
        </p>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="product-grid">
          {products.map((product) => (
            <ProductCard
              key={product.product_id}
              product={product}
            />
          ))}
        </div>
      )}
    </section>
  );
}