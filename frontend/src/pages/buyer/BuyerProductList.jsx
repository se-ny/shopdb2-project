import { useEffect, useState } from "react";
import { getBuyerProducts } from "../../api/buyer";
import "../../styles/buyer.css";

function money(value) {
  return `${Number(value || 0).toLocaleString("ko-KR")}원`;
}

export default function BuyerProductList({ onSelect }) {
  const [products, setProducts] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setError("");
        setProducts(await getBuyerProducts());
      } catch (err) {
        setError(err.message || "상품을 불러오지 못했습니다.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const filtered = products.filter((product) => {
    const search = keyword.trim().toLowerCase();

    if (!search) return true;

    return [
      product.product_name,
      product.product_code,
      product.category_name,
      product.seller_name,
    ]
      .filter(Boolean)
      .some((value) =>
        String(value).toLowerCase().includes(search),
      );
  });

  return (
    <section className="buyer-page">
      <div className="buyer-page-header">
        <div>
          <p className="buyer-eyebrow">SHOPDB2 STORE</p>
          <h1>상품 쇼핑</h1>
          <p>
            현재 판매 중인 상품을 확인하고 원하는 상품을 선택하세요.
          </p>
        </div>
      </div>

      <div className="buyer-shop-toolbar">
        <input
          type="search"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          placeholder="상품명, 상품코드, 카테고리 검색"
          aria-label="상품 검색"
        />

        <span>
          {filtered.length}개 상품
        </span>
      </div>

      {loading && (
        <div className="buyer-state">
          상품을 불러오는 중입니다.
        </div>
      )}

      {error && (
        <div className="buyer-alert buyer-alert--error">
          {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="buyer-empty">
          <strong>조건에 맞는 상품이 없습니다.</strong>
          <p>다른 검색어를 입력해 보세요.</p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="buyer-product-grid">
          {filtered.map((product) => {
            const imageUrl =
              product.main_image_url ||
              product.thumbnail_url ||
              null;

            return (
              <button
                type="button"
                className="buyer-product-card"
                key={product.product_id}
                onClick={() => onSelect?.(product.product_id)}
              >
                <div className="buyer-product-image">
                  {imageUrl ? (
                    <img
                      src={imageUrl}
                      alt={product.product_name || "상품 이미지"}
                    />
                  ) : (
                    <span>NO IMAGE</span>
                  )}
                </div>

                <div className="buyer-product-body">
                  <p className="buyer-product-meta">
                    {product.category_name || "상품"}
                    {product.seller_name
                      ? ` · ${product.seller_name}`
                      : ""}
                  </p>

                  <h3>{product.product_name}</h3>

                  {product.short_description && (
                    <p className="buyer-product-description">
                      {product.short_description}
                    </p>
                  )}

                  <div className="buyer-product-price">
                    <strong>
                      {money(product.sale_price)}
                    </strong>

                    {Number(product.regular_price) !==
                      Number(product.sale_price) && (
                      <span>
                        {money(product.regular_price)}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}
