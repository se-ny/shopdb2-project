import "../styles/product.css";

function formatPrice(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return `${number.toLocaleString("ko-KR")}원`;
}

export default function ProductCard({ product, onClick }) {
  const imageUrl =
    product.thumbnail_url || product.main_image_url || null;

  return (
    <article
      className="product-card"
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(event) => {
        if (onClick && (event.key === "Enter" || event.key === " ")) {
          onClick();
        }
      }}
    >
      <div className="product-card__image-wrap">
        {imageUrl ? (
          <img
            className="product-card__image"
            src={imageUrl}
            alt={product.product_name || "상품 이미지"}
            onError={(event) => {
              event.currentTarget.style.display = "none";
            }}
          />
        ) : (
          <div className="product-card__image-placeholder">
            NO IMAGE
          </div>
        )}
      </div>

      <div className="product-card__body">
        <div className="product-card__category">
          {product.category_name || "카테고리 없음"}
        </div>

        <h3>{product.product_name}</h3>

        <p className="product-card__seller">
          판매자: {product.seller_name || "정보 없음"}
        </p>

        <div className="product-card__price">
          <span className="product-card__sale-price">
            {formatPrice(product.sale_price)}
          </span>

          {product.regular_price !== undefined &&
            product.regular_price !== null &&
            Number(product.regular_price) !== Number(product.sale_price) && (
              <span className="product-card__regular-price">
                {formatPrice(product.regular_price)}
              </span>
            )}
        </div>
      </div>
    </article>
  );
}