import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

function ProductDetail({ productId, onClose }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadProductDetail() {
      try {
        setLoading(true);
        setErrorMessage("");

        const response = await fetch(
          `${API_BASE_URL}/api/products/${productId}`
        );

        if (!response.ok) {
          throw new Error(
            `상품 상세 조회 실패: HTTP ${response.status}`
          );
        }

        const data = await response.json();
        setProduct(data);
      } catch (error) {
        setErrorMessage(error.message);
      } finally {
        setLoading(false);
      }
    }

    loadProductDetail();
  }, [productId]);

  if (loading) {
    return <p>상품 상세정보를 불러오는 중입니다.</p>;
  }

  if (errorMessage) {
    return <p className="error-message">{errorMessage}</p>;
  }

  if (!product) {
    return null;
  }

  return (
    <section className="product-detail">
      <button
        type="button"
        className="detail-close-button"
        onClick={onClose}
      >
        목록으로
      </button>

      <div className="product-detail-layout">
        <div>
          {product.image?.public_url && (
            <img
              className="product-detail-image"
              src={product.image.public_url}
              alt={product.image.alt_text || product.product_name}
            />
          )}
        </div>

        <div>
          <p className="product-category">
            {product.category?.category_name}
          </p>

          <h2>{product.product_name}</h2>

          <p>{product.description}</p>

          <p className="regular-price">
            정상가{" "}
            {Number(product.regular_price).toLocaleString()}원
          </p>

          <strong className="sale-price">
            판매가{" "}
            {Number(product.sale_price).toLocaleString()}원
          </strong>

          <p className="product-code">
            상품코드: {product.product_code}
          </p>
        </div>
      </div>

      <div className="variant-section">
        <h3>상품 옵션 및 재고</h3>

        {product.variants.map((variant) => (
          <div className="variant-card" key={variant.variant_id}>
            <strong>{variant.sku_code}</strong>

            <p>
              {variant.option_name1}: {variant.option_value1}
            </p>

            {variant.option_name2 && (
              <p>
                {variant.option_name2}: {variant.option_value2}
              </p>
            )}

            <p>
              추가금액:{" "}
              {Number(variant.additional_price).toLocaleString()}원
            </p>

            <p>현재 재고: {variant.stock_quantity}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default ProductDetail;