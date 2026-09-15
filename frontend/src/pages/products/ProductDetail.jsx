import { useEffect, useState } from "react";
import {
  getProduct,
  getProductInventory,
  getProductVariants,
  updateProductInventory,
  updateProductVariant,
  deleteProductVariant,
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
  const [variantDrafts, setVariantDrafts] = useState({});
  const [loading, setLoading] = useState(true);
  const [savingInventoryId, setSavingInventoryId] = useState(null);
  const [savingVariantId, setSavingVariantId] = useState(null);
  const [deletingVariantId, setDeletingVariantId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadProductDetail() {
      try {
        await Promise.resolve();

        if (!productId) {
          if (!cancelled) {
            setError("상품 ID가 없습니다.");
            setLoading(false);
          }
          return;
        }

        const [productData, variantData, inventoryData] =
          await Promise.all([
            getProduct(productId),
            getProductVariants(productId),
            getProductInventory(productId),
          ]);

        if (cancelled) {
          return;
        }

        setProduct(productData);
        setVariants(variantData);
        setInventory(inventoryData);
        setError("");
        setMessage("");

        const inventoryDraftData = {};

        inventoryData.forEach((item) => {
          inventoryDraftData[item.inventory_id] = {
            stock_quantity: item.stock_quantity,
            safety_stock: item.safety_stock,
          };
        });

        setInventoryDrafts(inventoryDraftData);

        const variantDraftData = {};

        variantData.forEach((variant) => {
          variantDraftData[variant.variant_id] = {
            sku_code: variant.sku_code,
            option_name1: variant.option_name1 || "",
            option_value1: variant.option_value1 || "",
            option_name2: variant.option_name2 || "",
            option_value2: variant.option_value2 || "",
            additional_price: variant.additional_price,
            active_yn: variant.active_yn,
          };
        });

        setVariantDrafts(variantDraftData);
        setLoading(false);
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "상품 상세 정보를 불러오지 못했습니다.",
          );
          setLoading(false);
        }
      }
    }

    loadProductDetail();

    return () => {
      cancelled = true;
    };
  }, [productId]);

  function handleInventoryChange(
    inventoryId,
    field,
    value,
  ) {
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
      setError(
        err.message || "재고 수정에 실패했습니다.",
      );
    } finally {
      setSavingInventoryId(null);
    }
  }

  function handleVariantChange(
    variantId,
    field,
    value,
  ) {
    setVariantDrafts((current) => ({
      ...current,
      [variantId]: {
        ...current[variantId],
        [field]: value,
      },
    }));
  }

  async function handleVariantSave(variant) {
    try {
      setSavingVariantId(variant.variant_id);
      setError("");
      setMessage("");

      const draft = variantDrafts[variant.variant_id];

      const updated = await updateProductVariant(
        productId,
        variant.variant_id,
        {
          sku_code: draft.sku_code,
          option_name1: draft.option_name1 || null,
          option_value1: draft.option_value1 || null,
          option_name2: draft.option_name2 || null,
          option_value2: draft.option_value2 || null,
          additional_price: Number(
            draft.additional_price,
          ),
          active_yn: draft.active_yn,
        },
      );

      setVariants((current) =>
        current.map((currentVariant) =>
          currentVariant.variant_id === variant.variant_id
            ? updated
            : currentVariant,
        ),
      );

      setVariantDrafts((current) => ({
        ...current,
        [variant.variant_id]: {
          sku_code: updated.sku_code,
          option_name1: updated.option_name1 || "",
          option_value1: updated.option_value1 || "",
          option_name2: updated.option_name2 || "",
          option_value2: updated.option_value2 || "",
          additional_price: updated.additional_price,
          active_yn: updated.active_yn,
        },
      }));

      setMessage(
        `옵션이 수정되었습니다. (${updated.sku_code})`,
      );
    } catch (err) {
      setError(
        err.message || "옵션 수정에 실패했습니다.",
      );
    } finally {
      setSavingVariantId(null);
    }
  }

  async function handleVariantDelete(variant) {
    try {
      setDeletingVariantId(variant.variant_id);
      setError("");
      setMessage("");

      const updated = await deleteProductVariant(
        productId,
        variant.variant_id,
      );

      setVariants((current) =>
        current.map((currentVariant) =>
          currentVariant.variant_id === variant.variant_id
            ? updated
            : currentVariant,
        ),
      );

      setVariantDrafts((current) => ({
        ...current,
        [variant.variant_id]: {
          ...current[variant.variant_id],
          active_yn: updated.active_yn,
        },
      }));

      setMessage(
        `옵션이 비활성화되었습니다. (${updated.sku_code})`,
      );
    } catch (err) {
      setError(
        err.message ||
          "옵션 비활성화에 실패했습니다.",
      );
    } finally {
      setDeletingVariantId(null);
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
              alt={
                product.product_name || "상품 이미지"
              }
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
            판매자:{" "}
            {product.seller_name || "정보 없음"}
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

      {(error || message) && (
        <div>
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
        </div>
      )}

      <div>
        <h2>상품 옵션 관리</h2>

        {variants.length === 0 ? (
          <p className="product-state">
            등록된 옵션이 없습니다.
          </p>
        ) : (
          <div>
            {variants.map((variant) => {
              const draft =
                variantDrafts[variant.variant_id] || {
                  sku_code: variant.sku_code,
                  option_name1:
                    variant.option_name1 || "",
                  option_value1:
                    variant.option_value1 || "",
                  option_name2:
                    variant.option_name2 || "",
                  option_value2:
                    variant.option_value2 || "",
                  additional_price:
                    variant.additional_price,
                  active_yn: variant.active_yn,
                };

              return (
                <div key={variant.variant_id}>
                  <label>
                    SKU 코드
                    <input
                      type="text"
                      value={draft.sku_code}
                      onChange={(event) =>
                        handleVariantChange(
                          variant.variant_id,
                          "sku_code",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    옵션명 1
                    <input
                      type="text"
                      value={draft.option_name1}
                      onChange={(event) =>
                        handleVariantChange(
                          variant.variant_id,
                          "option_name1",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    옵션값 1
                    <input
                      type="text"
                      value={draft.option_value1}
                      onChange={(event) =>
                        handleVariantChange(
                          variant.variant_id,
                          "option_value1",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    옵션명 2
                    <input
                      type="text"
                      value={draft.option_name2}
                      onChange={(event) =>
                        handleVariantChange(
                          variant.variant_id,
                          "option_name2",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    옵션값 2
                    <input
                      type="text"
                      value={draft.option_value2}
                      onChange={(event) =>
                        handleVariantChange(
                          variant.variant_id,
                          "option_value2",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    추가 금액
                    <input
                      type="number"
                      min="0"
                      value={draft.additional_price}
                      onChange={(event) =>
                        handleVariantChange(
                          variant.variant_id,
                          "additional_price",
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <label>
                    상태
                    <select
                      value={draft.active_yn}
                      onChange={(event) =>
                        handleVariantChange(
                          variant.variant_id,
                          "active_yn",
                          event.target.value,
                        )
                      }
                    >
                      <option value="Y">활성</option>
                      <option value="N">비활성</option>
                    </select>
                  </label>

                  <button
                    type="button"
                    onClick={() =>
                      handleVariantSave(variant)
                    }
                    disabled={
                      savingVariantId ===
                      variant.variant_id
                    }
                  >
                    {savingVariantId ===
                    variant.variant_id
                      ? "저장 중..."
                      : "옵션 저장"}
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      handleVariantDelete(variant)
                    }
                    disabled={
                      deletingVariantId ===
                        variant.variant_id ||
                      variant.active_yn === "N"
                    }
                  >
                    {deletingVariantId ===
                    variant.variant_id
                      ? "처리 중..."
                      : "옵션 비활성화"}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div>
        <h2>재고 관리</h2>

        {inventory.length === 0 ? (
          <p className="product-state">
            등록된 재고 정보가 없습니다.
          </p>
        ) : (
          <div>
            {inventory.map((item) => {
              const draft =
                inventoryDrafts[item.inventory_id] || {
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
                    onClick={() =>
                      handleInventorySave(item)
                    }
                    disabled={
                      savingInventoryId ===
                      item.inventory_id
                    }
                  >
                    {savingInventoryId ===
                    item.inventory_id
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