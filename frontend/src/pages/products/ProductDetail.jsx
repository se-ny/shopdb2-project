import { useEffect, useState } from "react";
import {
  getProduct,
  getProductInventory,
  getProductVariants,
  updateProductInventory,
} from "../../api/products";
import "../../styles/product.css";

function formatPrice(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return `${number.toLocaleString("ko-KR")}원`;
}

export default function ProductDetail({ productId }) {
  const [product, setProduct] = useState(null);
  const [variants, setVariants] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [inventoryDrafts, setInventoryDrafts] = useState({});
  const [loading, setLoading] = useState(true);
  const [savingInventoryId, setSavingInventoryId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!productId) {
      setError("상품 ID가 없습니다.");
      setLoading(false);
      return;
    }

    async function loadProductDetail() {
      try {
        setLoading(true);
        setError("");
        setMessage("");

        const [productData, variantData, inventoryData] =
          await Promise.all([
            getProduct(productId),
            getProductVariants(productId),
            getProductInventory(productId),
          ]);

        setProduct(productData);
        setVariants(variantData);
        setInventory(inventoryData);

        const drafts = {};

        inventoryData.forEach((item) => {
          drafts[item.inventory_id] = {
            stock_quantity: item.stock_quantity,
            safety_stock: item.safety_stock,
          };
        });

        setInventoryDrafts(drafts);
      } catch (err) {
        setError(
          err.message || "상품 상세 정보를 불러오지 못했습니다.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadProductDetail();
  }, [productId]);

  function handleInventoryChange(inventoryId, field, value) {
    setInventoryDrafts((current) => ({
      ...current,
      [inventoryId]: {
        ...current[inventoryId],
        [field]: value,
      },
    }));
  }

  async function handleInventorySave(item) {
    try {
      setSavingInventoryId(item.inventory_id);
      setError("");
      setMessage("");

      const draft = inventoryDrafts[item.inventory_id];

      const updated = await updateProductInventory(
        productId,
        item.inventory_id,
        {
          stock_quantity: Number(draft.stock_quantity),
          safety_stock: Number(draft.safety_stock),
        },
      );

      setInventory((current) =>
        current.map((inventoryItem) =>
          inventoryItem.inventory_id === item.inventory_id
            ? updated
            : inventoryItem,
        ),
      );

      setInventoryDrafts((current) => ({
        ...current,
        [item.inventory_id]: {
          stock_quantity: updated.stock_quantity,
          safety_stock: updated.safety_stock,
        },
      }));

      setMessage(
        `재고가 수정되었습니다. (${updated.org_name})`,
      );
    } catch (err) {
      setError(err.message || "재고 수정에 실패했습니다.");
    } finally {
      setSavingInventoryId(null);
    }
  }

  if (loading) {
    return (
      <section className="product-page">
        <p className="product-state">
          상품 상세 정보를 불러오는 중입니다.
        </p>
      </section>
    );
  }

  if (error && !product) {
    return (
      <section className="product-page">
        <p className="product-state product-state--error">
          {error}
        </p>
      </section>
    );
  }

  if (!product) {
    return (
      <section className="product-page">
        <p className="product-state">
          상품 정보가 없습니다.
        </p>
      </section>
    );
  }

  const imageUrl =
    product.main_image_url ||
    product.thumbnail_url ||
    null;

  return (
    <section className="product-page">
      <div className="product-detail">
        <div className="product-detail__image-wrap">
          {imageUrl ? (
            <img
              className="product-card__image"
              src={imageUrl}
              alt={product.product_name || "상품 이미지"}
            />
          ) : (
            <div className="product-card__image-placeholder">
              NO IMAGE
            </div>
          )}
        </div>

        <div className="product-detail__info">
          <p className="product-page__eyebrow">
            {product.category_name || "상품"}
          </p>

          <h1>{product.product_name}</h1>

          <p>상품코드: {product.product_code}</p>

          <p>
            판매자: {product.seller_name || "정보 없음"}
          </p>

          {product.short_description && (
            <p>{product.short_description}</p>
          )}

          {product.description && (
            <p>{product.description}</p>
          )}

          <div className="product-card__price">
            <strong className="product-card__sale-price">
              {formatPrice(product.sale_price)}
            </strong>

            {Number(product.regular_price) !==
              Number(product.sale_price) && (
              <span className="product-card__regular-price">
                {formatPrice(product.regular_price)}
              </span>
            )}
          </div>

          <p>
            상품 상태: {product.product_status}
          </p>
        </div>
      </div>

      <div>
        <h2>상품 옵션</h2>

        {variants.length === 0 ? (
          <p className="product-state">
            등록된 옵션이 없습니다.
          </p>
        ) : (
          <div>
            {variants.map((variant) => (
              <div key={variant.variant_id}>
                <strong>{variant.sku_code}</strong>

                <p>
                  {variant.option_name1 &&
                    `${variant.option_name1}: `}
                  {variant.option_value1 || ""}

                  {variant.option_name2 && (
                    <>
                      {" / "}
                      {variant.option_name2}:{" "}
                      {variant.option_value2 || ""}
                    </>
                  )}
                </p>

                <p>
                  추가금액:{" "}
                  {formatPrice(variant.additional_price)}
                </p>

                <p>상태: {variant.active_yn}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2>재고 관리</h2>

        {error && (
          <p className="product-state product-state--error">
            {error}
          </p>
        )}

        {message && (
          <p className="product-state">
            {message}
          </p>
        )}

        {inventory.length === 0 ? (
          <p className="product-state">
            등록된 재고 정보가 없습니다.
          </p>
        ) : (
          <div>
            {inventory.map((item) => {
              const draft = inventoryDrafts[item.inventory_id] || {
                stock_quantity: item.stock_quantity,
                safety_stock: item.safety_stock,
              };

              return (
                <div key={item.inventory_id}>
                  <p>{item.org_name}</p>

                  <p>SKU: {item.variant_id}</p>

                  <label>
                    재고 수량
                    <input
                      type="number"
                      min="0"
                      value={draft.stock_quantity}
                      onChange={(event) =>
                        handleInventoryChange(
                          item.inventory_id,
                          "stock_quantity",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    안전재고
                    <input
                      type="number"
                      min="0"
                      value={draft.safety_stock}
                      onChange={(event) =>
                        handleInventoryChange(
                          item.inventory_id,
                          "safety_stock",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <p>
                    예약: {item.reserved_quantity}
                  </p>

                  <p>
                    현재 판매 가능 수량:{" "}
                    {item.available_quantity}
                  </p>

                  <button
                    type="button"
                    onClick={() => handleInventorySave(item)}
                    disabled={
                      savingInventoryId === item.inventory_id
                    }
                  >
                    {savingInventoryId === item.inventory_id
                      ? "저장 중..."
                      : "재고 저장"}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}