import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadProducts() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/products`);

        if (!response.ok) {
          throw new Error(`상품 조회 실패: HTTP ${response.status}`);
        }

        const data = await response.json();
        setProducts(data);
      } catch (error) {
        setErrorMessage(error.message);
      } finally {
        setLoading(false);
      }
    }

    loadProducts();
  }, []);

  if (loading) {
    return <p>상품을 불러오는 중입니다.</p>;
  }

  if (errorMessage) {
    return <p className="error-message">{errorMessage}</p>;
  }

  return (
    <section className="product-section">
      <h2>판매 중 상품</h2>
      <p>현재 구매 가능한 상품 {products.length}개</p>

      <div className="product-grid">
        {products.map((product) => (
          <article className="product-card" key={product.product_id}>
            <p className="product-category">{product.category_name}</p>

            <h3>{product.product_name}</h3>

            <p>{product.short_description}</p>

            <p className="regular-price">
              정상가 {Number(product.regular_price).toLocaleString()}원
            </p>

            <strong className="sale-price">
              판매가 {Number(product.sale_price).toLocaleString()}원
            </strong>

            <p className="product-code">
              상품코드: {product.product_code}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default ProductList;