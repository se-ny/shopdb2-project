import { useEffect, useMemo, useState } from "react";
import {
  addCartItem,
  getBuyerProductDetail,
} from "../../api/buyer";
import "../../styles/buyer.css";

function money(value) {
  return `${Number(value || 0).toLocaleString("ko-KR")}원`;
}

function variantLabel(variant) {
  const values = [
    variant.option_name1 && variant.option_value1
      ? `${variant.option_name1}: ${variant.option_value1}`
      : null,
    variant.option_name2 && variant.option_value2
      ? `${variant.option_name2}: ${variant.option_value2}`
      : null,
  ].filter(Boolean);

  return values.length
    ? values.join(" / ")
    : variant.sku_code || `옵션 ${variant.variant_id}`;
}

export default function BuyerProductDetail({
  productId,
  onBack,
  onCart,
  onBuyNow,
  isAuthenticated,
  onRequireLogin,
}) {
  const [product, setProduct] = useState(null);
  const [selectedVariantId, setSelectedVariantId] =
    useState("");
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setError("");
        setMessage("");

        const data = await getBuyerProductDetail(productId);
        setProduct(data);

        const firstAvailable = (data.variants || []).find(
          (variant) =>
            Number(variant.available_quantity || 0) > 0,
        );

        if (firstAvailable) {
          setSelectedVariantId(
            String(firstAvailable.variant_id),
          );
        }
      } catch (err) {
        setError(
          err.message ||
            "상품 상세정보를 불러오지 못했습니다.",
        );
      } finally {
        setLoading(false);
      }
    })();
  }, [productId]);

  const selectedVariant = useMemo(
    () =>
      (product?.variants || []).find(
        (variant) =>
          String(variant.variant_id) ===
          String(selectedVariantId),
      ) || null,
    [product, selectedVariantId],
  );

  const availableQuantity = Number(
    selectedVariant?.available_quantity || 0,
  );

  const unitPrice =
    Number(product?.sale_price || 0) +
    Number(selectedVariant?.additional_price || 0);

  const totalPrice = unitPrice * quantity;

  const canPurchase =
    Boolean(selectedVariant) &&
    availableQuantity > 0 &&
    quantity >= 1 &&
    quantity <= availableQuantity;

  function selectVariant(event) {
    setSelectedVariantId(event.target.value);
    setQuantity(1);
    setError("");
    setMessage("");
  }

  function validateSelection() {
    if (!selectedVariant) {
      setError("구매할 옵션을 선택해 주세요.");
      return false;
    }

    if (availableQuantity <= 0) {
      setError("선택한 옵션은 현재 구매할 수 없습니다.");
      return false;
    }

    if (quantity > availableQuantity) {
      setError(
        `현재 구매 가능한 수량은 ${availableQuantity}개입니다.`,
      );
      return false;
    }

    return true;
  }

  async function handleAddCart() {
    if (!validateSelection()) return;

    if (!isAuthenticated) {
      onRequireLogin?.();
      return;
    }

    try {
      setWorking(true);
      setError("");
      setMessage("");

      await addCartItem(
        selectedVariant.variant_id,
        quantity,
      );

      setMessage(
        "장바구니에 담았습니다. 장바구니에서 현재 가격과 재고를 다시 확인할 수 있습니다.",
      );
    } catch (err) {
      setError(
        err.message ||
          "장바구니에 상품을 담지 못했습니다.",
      );
    } finally {
      setWorking(false);
    }
  }

  function handleBuyNow() {
    if (!validateSelection()) return;

    if (!isAuthenticated) {
      onRequireLogin?.();
      return;
    }

    onBuyNow?.({
      product_id: product.product_id,
      variant_id: selectedVariant.variant_id,
      product_name: product.product_name,
      option_name1: selectedVariant.option_name1,
      option_value1: selectedVariant.option_value1,
      option_name2: selectedVariant.option_name2,
      option_value2: selectedVariant.option_value2,
      current_unit_price: unitPrice,
      quantity,
      available_quantity: availableQuantity,
      purchasable: true,
    });
  }

  if (loading) {
    return (
      <div className="buyer-page">
        <div className="buyer-state">
          상품 상세정보를 불러오는 중입니다.
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="buyer-page">
        <div className="buyer-alert buyer-alert--error">
          {error || "상품 정보를 찾을 수 없습니다."}
        </div>

        <button
          type="button"
          className="buyer-secondary-button"
          onClick={onBack}
        >
          상품 목록으로
        </button>
      </div>
    );
  }

  const imageUrl =
    product.image?.public_url ||
    product.image?.thumbnail_url ||
    product.main_image_url ||
    product.thumbnail_url ||
    null;

  const imageAlt =
    product.image?.alt_text ||
    product.product_name ||
    "상품 이미지";

  return (
    <section className="buyer-page">
      <button
        type="button"
        className="buyer-back-button"
        onClick={onBack}
      >
        ← 상품 목록
      </button>

      <div className="buyer-detail-grid">
        <div className="buyer-detail-image">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={imageAlt}
            />
          ) : (
            <span>NO IMAGE</span>
          )}
        </div>

        <div className="buyer-detail-info">
          <p className="buyer-eyebrow">
            {product.category_name || "PRODUCT"}
          </p>

          <h1>{product.product_name}</h1>

          <p className="buyer-muted">
            {product.seller_name || ""}
          </p>

          {product.short_description && (
            <p className="buyer-detail-description">
              {product.short_description}
            </p>
          )}

          <div className="buyer-detail-price">
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

          <div className="buyer-purchase-box">
            <label>
              옵션
              <select
                value={selectedVariantId}
                onChange={selectVariant}
              >
                <option value="">
                  옵션을 선택하세요
                </option>

                {(product.variants || []).map(
                  (variant) => {
                    const available = Number(
                      variant.available_quantity || 0,
                    );

                    return (
                      <option
                        key={variant.variant_id}
                        value={variant.variant_id}
                        disabled={available <= 0}
                      >
                        {variantLabel(variant)}
                        {Number(
                          variant.additional_price || 0,
                        ) > 0
                          ? ` (+${money(
                              variant.additional_price,
                            )})`
                          : ""}
                        {available <= 0 ? " - 품절" : ""}
                      </option>
                    );
                  },
                )}
              </select>
            </label>

            <label>
              수량
              <div className="buyer-quantity buyer-detail-quantity">
                <button
                  type="button"
                  onClick={() =>
                    setQuantity((value) =>
                      Math.max(1, value - 1),
                    )
                  }
                  disabled={quantity <= 1}
                >
                  −
                </button>

                <span>{quantity}</span>

                <button
                  type="button"
                  onClick={() =>
                    setQuantity((value) =>
                      Math.min(
                        availableQuantity || 1,
                        value + 1,
                      ),
                    )
                  }
                  disabled={
                    !selectedVariant ||
                    quantity >= availableQuantity
                  }
                >
                  +
                </button>
              </div>
            </label>

            {selectedVariant && (
              <div className="buyer-stock-info">
                <span>현재 구매 가능</span>
                <strong>{availableQuantity}개</strong>
              </div>
            )}

            <div className="buyer-purchase-total">
              <span>예상 상품금액</span>
              <strong>{money(totalPrice)}</strong>
            </div>

            {error && (
              <div className="buyer-alert buyer-alert--error">
                {error}
              </div>
            )}

            {message && (
              <div className="buyer-alert buyer-alert--success">
                {message}

                <button
                  type="button"
                  className="buyer-inline-action"
                  onClick={onCart}
                >
                  장바구니 보기
                </button>
              </div>
            )}

            <div className="buyer-purchase-actions">
              <button
                type="button"
                className="buyer-secondary-button"
                onClick={handleAddCart}
                disabled={!canPurchase || working}
              >
                {working
                  ? "담는 중..."
                  : "장바구니 담기"}
              </button>

              <button
                type="button"
                className="buyer-primary-button"
                onClick={handleBuyNow}
                disabled={!canPurchase || working}
              >
                바로구매
              </button>
            </div>
          </div>
        </div>
      </div>

      {product.description && (
        <div className="buyer-product-content">
          <h2>상품 설명</h2>
          <p>{product.description}</p>
        </div>
      )}
    </section>
  );
}
