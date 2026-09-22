import { useEffect, useState } from "react";
import ProductImageManager from "../../components/ProductImageManager";
import {
  createProductVariant,
  deleteProduct,
  deleteProductVariant,
  getProduct,
  getProductFiles,
  getProductInventory,
  getProductVariants,
  restoreProduct,
  updateProduct,
  updateProductInventory,
  updateProductVariant,
} from "../../api/products";
import "../../styles/product.css";

const CATEGORY_OPTIONS = [
  { id: 1, name: "전자제품" },
  { id: 2, name: "패션" },
  { id: 3, name: "노트북" },
  { id: 4, name: "스마트폰" },
  { id: 5, name: "상의" },
  { id: 6, name: "신발" },
];

const EMPTY_VARIANT = {
  sku_code: "",
  option_name1: "",
  option_value1: "",
  option_name2: "",
  option_value2: "",
  additional_price: 0,
};

function formatPrice(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return `${number.toLocaleString("ko-KR")}원`;
}

export default function ProductDetail({ productId }) {
  const [product, setProduct] = useState(null);
  const [productDraft, setProductDraft] = useState(null);

  const [variants, setVariants] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [productFiles, setProductFiles] = useState([]);

  const [inventoryDrafts, setInventoryDrafts] =
    useState({});

  const [variantDrafts, setVariantDrafts] =
    useState({});

  const [newVariant, setNewVariant] =
    useState(EMPTY_VARIANT);

  const [loading, setLoading] = useState(true);

  const [savingProduct, setSavingProduct] =
    useState(false);

  const [deletingProduct, setDeletingProduct] =
    useState(false);

  const [restoringProduct, setRestoringProduct] =
    useState(false);

  const [creatingVariant, setCreatingVariant] =
    useState(false);

  const [savingInventoryId, setSavingInventoryId] =
    useState(null);

  const [savingVariantId, setSavingVariantId] =
    useState(null);

  const [deletingVariantId, setDeletingVariantId] =
    useState(null);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadProductDetail() {
      try {
        if (!productId) {
          if (!cancelled) {
            setError("상품 ID가 없습니다.");
            setLoading(false);
          }

          return;
        }

        const [
          productData,
          variantData,
          inventoryData,
          fileData,
        ] = await Promise.all([
          getProduct(productId),
          getProductVariants(productId),
          getProductInventory(productId),
          getProductFiles(productId),
        ]);

        if (cancelled) {
          return;
        }

        setProduct(productData);

        setProductDraft({
          category_id: productData.category_id,
          product_name:
            productData.product_name || "",
          short_description:
            productData.short_description || "",
          description:
            productData.description || "",
          regular_price:
            productData.regular_price ?? "",
          sale_price:
            productData.sale_price ?? "",
          product_status:
            productData.product_status || "READY",
        });

        setVariants(variantData);
        setInventory(inventoryData);
        setProductFiles(fileData);

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
        });

        setVariantDrafts(variantDraftData);

        setError("");
        setMessage("");
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "상품 상세 정보를 불러오지 못했습니다.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadProductDetail();

    return () => {
      cancelled = true;
    };
  }, [productId]);

  function handleProductChange(event) {
    const { name, value } = event.target;

    setProductDraft((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleProductSave() {
    if (!productDraft) {
      return;
    }

    const regularPrice = Number(
      productDraft.regular_price,
    );

    const salePrice = Number(
      productDraft.sale_price,
    );

    if (!productDraft.product_name.trim()) {
      setError("상품명을 입력해주세요.");
      return;
    }

    if (regularPrice <= 0 || salePrice <= 0) {
      setError(
        "정상가와 판매가는 0보다 커야 합니다.",
      );
      return;
    }

    if (salePrice > regularPrice) {
      setError(
        "판매가는 정상가보다 높을 수 없습니다.",
      );
      return;
    }

    try {
      setSavingProduct(true);
      setError("");
      setMessage("");

      const updated = await updateProduct(
        productId,
        {
          category_id: Number(
            productDraft.category_id,
          ),
          product_name:
            productDraft.product_name.trim(),
          short_description:
            productDraft.short_description.trim() ||
            null,
          description:
            productDraft.description.trim() || null,
          regular_price: regularPrice,
          sale_price: salePrice,
          product_status:
            productDraft.product_status,
        },
      );

      setProduct(updated);

      setProductDraft({
        category_id: updated.category_id,
        product_name:
          updated.product_name || "",
        short_description:
          updated.short_description || "",
        description:
          updated.description || "",
        regular_price:
          updated.regular_price ?? "",
        sale_price:
          updated.sale_price ?? "",
        product_status:
          updated.product_status || "READY",
      });

      setMessage("상품 정보가 수정되었습니다.");
    } catch (err) {
      setError(
        err.message ||
          "상품 수정에 실패했습니다.",
      );
    } finally {
      setSavingProduct(false);
    }
  }

  async function handleProductDelete() {
    const confirmed = window.confirm(
      "이 상품을 삭제 처리하시겠습니까?\n실제 행 삭제가 아니라 DELETED 상태로 변경됩니다.",
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingProduct(true);
      setError("");
      setMessage("");

      if (!product?.seller_user_id) {
        throw new Error(
          "판매자 사용자 ID를 확인할 수 없습니다.",
        );
      }

      await deleteProduct(
        productId,
        product.seller_user_id,
      );

      setProduct((current) => ({
        ...current,
        product_status: "DELETED",
      }));

      setProductDraft((current) => ({
        ...current,
        product_status: "DELETED",
      }));

      setMessage(
        "상품이 삭제 상태(DELETED)로 변경되었습니다.",
      );
    } catch (err) {
      setError(
        err.message ||
          "상품 삭제 처리에 실패했습니다.",
      );
    } finally {
      setDeletingProduct(false);
    }
  }

  async function handleProductRestore() {
    const confirmed = window.confirm(
      "이 상품을 복원하시겠습니까?\n복원 후 상품 상태는 판매 준비(READY)로 변경됩니다.",
    );

    if (!confirmed) {
      return;
    }

    try {
      setRestoringProduct(true);
      setError("");
      setMessage("");

      if (!product?.seller_user_id) {
        throw new Error(
          "판매자 사용자 ID를 확인할 수 없습니다.",
        );
      }

      const restored = await restoreProduct(
        productId,
        product.seller_user_id,
      );

      setProduct(restored);

      setProductDraft((current) => ({
        ...current,
        product_status:
          restored.product_status || "READY",
      }));

      setMessage(
        "상품이 복원되었습니다. 상품 상태는 판매 준비(READY)입니다.",
      );
    } catch (err) {
      setError(
        err.message ||
          "상품 복원에 실패했습니다.",
      );
    } finally {
      setRestoringProduct(false);
    }
  }

  function handleNewVariantChange(event) {
    const { name, value } = event.target;

    setNewVariant((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleCreateVariant(event) {
    event.preventDefault();

    if (!newVariant.sku_code.trim()) {
      setError("SKU 코드를 입력해주세요.");
      return;
    }

    if (
      Number(newVariant.additional_price) < 0
    ) {
      setError(
        "추가 금액은 0 이상이어야 합니다.",
      );
      return;
    }

    try {
      setCreatingVariant(true);
      setError("");
      setMessage("");

      const created =
        await createProductVariant(productId, {
          product_id: Number(productId),
          sku_code:
            newVariant.sku_code.trim(),
          option_name1:
            newVariant.option_name1.trim() ||
            null,
          option_value1:
            newVariant.option_value1.trim() ||
            null,
          option_name2:
            newVariant.option_name2.trim() ||
            null,
          option_value2:
            newVariant.option_value2.trim() ||
            null,
          additional_price: Number(
            newVariant.additional_price,
          ),
        });

      setVariants((current) => [
        ...current,
        created,
      ]);

      setVariantDrafts((current) => ({
        ...current,
        [created.variant_id]: {
          sku_code: created.sku_code,
          option_name1:
            created.option_name1 || "",
          option_value1:
            created.option_value1 || "",
          option_name2:
            created.option_name2 || "",
          option_value2:
            created.option_value2 || "",
          additional_price:
            created.additional_price,
          active_yn: created.active_yn,
        },
      }));

      setNewVariant(EMPTY_VARIANT);

      setMessage(
        `옵션이 등록되었습니다. (${created.sku_code})`,
      );
    } catch (err) {
      setError(
        err.message ||
          "옵션 등록에 실패했습니다.",
      );
    } finally {
      setCreatingVariant(false);
    }
  }

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

      const draft =
        inventoryDrafts[item.inventory_id];

      if (!product?.seller_user_id) {
        throw new Error(
          "판매자 사용자 ID를 확인할 수 없습니다.",
        );
      }

      const updated = await updateProductInventory(
        productId,
        item.inventory_id,
        {
          stock_quantity: Number(
            draft.stock_quantity,
          ),
          safety_stock: Number(
            draft.safety_stock,
          ),
        },
        product.seller_user_id,
      );

      setInventory((current) =>
        current.map((inventoryItem) =>
          inventoryItem.inventory_id ===
          item.inventory_id
            ? updated
            : inventoryItem,
        ),
      );

      setInventoryDrafts((current) => ({
        ...current,
        [item.inventory_id]: {
          stock_quantity:
            updated.stock_quantity,
          safety_stock:
            updated.safety_stock,
        },
      }));

      setMessage(
        `재고가 수정되었습니다. (${updated.org_name})`,
      );
    } catch (err) {
      setError(
        err.message ||
          "재고 수정에 실패했습니다.",
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

      const draft =
        variantDrafts[variant.variant_id];

      const updated = await updateProductVariant(
        productId,
        variant.variant_id,
        {
          sku_code: draft.sku_code,
          option_name1:
            draft.option_name1 || null,
          option_value1:
            draft.option_value1 || null,
          option_name2:
            draft.option_name2 || null,
          option_value2:
            draft.option_value2 || null,
          additional_price: Number(
            draft.additional_price,
          ),
          active_yn: draft.active_yn,
        },
      );

      setVariants((current) =>
        current.map((currentVariant) =>
          currentVariant.variant_id ===
          variant.variant_id
            ? updated
            : currentVariant,
        ),
      );

      setVariantDrafts((current) => ({
        ...current,
        [variant.variant_id]: {
          sku_code: updated.sku_code,
          option_name1:
            updated.option_name1 || "",
          option_value1:
            updated.option_value1 || "",
          option_name2:
            updated.option_name2 || "",
          option_value2:
            updated.option_value2 || "",
          additional_price:
            updated.additional_price,
          active_yn: updated.active_yn,
        },
      }));

      setMessage(
        `옵션이 수정되었습니다. (${updated.sku_code})`,
      );
    } catch (err) {
      setError(
        err.message ||
          "옵션 수정에 실패했습니다.",
      );
    } finally {
      setSavingVariantId(null);
    }
  }

  async function handleVariantDelete(variant) {
    try {
      setDeletingVariantId(
        variant.variant_id,
      );

      setError("");
      setMessage("");

      const updated =
        await deleteProductVariant(
          productId,
          variant.variant_id,
        );

      setVariants((current) =>
        current.map((currentVariant) =>
          currentVariant.variant_id ===
          variant.variant_id
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

  if (!product || !productDraft) {
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
                product.product_name ||
                "상품 이미지"
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
            상품 정보 수정
          </p>

          <p>
            상품코드: {product.product_code}
          </p>

          <p>
            판매자:{" "}
            {product.seller_name || "정보 없음"}
          </p>

          <label>
            카테고리
            <select
              name="category_id"
              value={productDraft.category_id}
              onChange={handleProductChange}
            >
              {CATEGORY_OPTIONS.map(
                (category) => (
                  <option
                    key={category.id}
                    value={category.id}
                  >
                    {category.name}
                  </option>
                ),
              )}
            </select>
          </label>

          <label>
            상품명
            <input
              type="text"
              name="product_name"
              value={
                productDraft.product_name
              }
              onChange={handleProductChange}
            />
          </label>

          <label>
            짧은 설명
            <input
              type="text"
              name="short_description"
              value={
                productDraft.short_description
              }
              onChange={handleProductChange}
            />
          </label>

          <label>
            상세 설명
            <textarea
              name="description"
              value={productDraft.description}
              onChange={handleProductChange}
              rows={5}
            />
          </label>

          <label>
            정상가
            <input
              type="number"
              name="regular_price"
              min="1"
              value={
                productDraft.regular_price
              }
              onChange={handleProductChange}
            />
          </label>

          <label>
            판매가
            <input
              type="number"
              name="sale_price"
              min="1"
              value={productDraft.sale_price}
              onChange={handleProductChange}
            />
          </label>

          <label>
            상품 상태
            <select
              name="product_status"
              value={
                productDraft.product_status
              }
              onChange={handleProductChange}
            >
              <option value="READY">
                판매 준비
              </option>

              <option value="SALE">
                판매 중
              </option>

              <option value="SOLD_OUT">
                품절
              </option>

              <option value="STOPPED">
                판매 중지
              </option>

              <option value="DELETED">
                삭제 상태
              </option>
            </select>
          </label>

          <div className="product-card__price">
            <strong className="product-card__sale-price">
              {formatPrice(
                product.sale_price,
              )}
            </strong>

            {Number(
              product.regular_price,
            ) !==
              Number(product.sale_price) && (
              <span className="product-card__regular-price">
                {formatPrice(
                  product.regular_price,
                )}
              </span>
            )}
          </div>

          <div
            style={{
              display: "flex",
              gap: "10px",
              marginTop: "16px",
              flexWrap: "wrap",
            }}
          >
            <button
              type="button"
              onClick={handleProductSave}
              disabled={
                savingProduct ||
                deletingProduct ||
                restoringProduct
              }
            >
              {savingProduct
                ? "상품 저장 중..."
                : "상품 저장"}
            </button>

            {product.product_status !==
              "DELETED" ? (
              <button
                type="button"
                onClick={handleProductDelete}
                disabled={
                  deletingProduct ||
                  restoringProduct
                }
              >
                {deletingProduct
                  ? "삭제 처리 중..."
                  : "상품 삭제"}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleProductRestore}
                disabled={restoringProduct}
              >
                {restoringProduct
                  ? "복원 처리 중..."
                  : "상품 복원"}
              </button>
            )}
          </div>
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
        <h2>신규 옵션 등록</h2>

        <form
          onSubmit={handleCreateVariant}
          style={{
            display: "grid",
            gap: "10px",
            marginBottom: "28px",
          }}
        >
          <label>
            SKU 코드
            <input
              type="text"
              name="sku_code"
              value={newVariant.sku_code}
              onChange={handleNewVariantChange}
              placeholder="예: NOTEBOOK-BLACK-16GB"
            />
          </label>

          <label>
            옵션명 1
            <input
              type="text"
              name="option_name1"
              value={newVariant.option_name1}
              onChange={handleNewVariantChange}
              placeholder="예: 색상"
            />
          </label>

          <label>
            옵션값 1
            <input
              type="text"
              name="option_value1"
              value={newVariant.option_value1}
              onChange={handleNewVariantChange}
              placeholder="예: 블랙"
            />
          </label>

          <label>
            옵션명 2
            <input
              type="text"
              name="option_name2"
              value={newVariant.option_name2}
              onChange={handleNewVariantChange}
              placeholder="예: 메모리"
            />
          </label>

          <label>
            옵션값 2
            <input
              type="text"
              name="option_value2"
              value={newVariant.option_value2}
              onChange={handleNewVariantChange}
              placeholder="예: 16GB"
            />
          </label>

          <label>
            추가 금액
            <input
              type="number"
              name="additional_price"
              min="0"
              value={
                newVariant.additional_price
              }
              onChange={handleNewVariantChange}
            />
          </label>

          <button
            type="submit"
            disabled={creatingVariant}
          >
            {creatingVariant
              ? "옵션 등록 중..."
              : "+ 옵션 등록"}
          </button>
        </form>

        <h2>상품 옵션 관리</h2>

        {variants.length === 0 ? (
          <p className="product-state">
            등록된 옵션이 없습니다.
          </p>
        ) : (
          <div>
            {variants.map((variant) => {
              const draft =
                variantDrafts[
                  variant.variant_id
                ] || {
                  sku_code:
                    variant.sku_code,
                  option_name1:
                    variant.option_name1 ||
                    "",
                  option_value1:
                    variant.option_value1 ||
                    "",
                  option_name2:
                    variant.option_name2 ||
                    "",
                  option_value2:
                    variant.option_value2 ||
                    "",
                  additional_price:
                    variant.additional_price,
                  active_yn:
                    variant.active_yn,
                };

              return (
                <div
                  key={variant.variant_id}
                >
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
                      value={
                        draft.option_name1
                      }
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
                      value={
                        draft.option_value1
                      }
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
                      value={
                        draft.option_name2
                      }
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
                      value={
                        draft.option_value2
                      }
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
                      value={
                        draft.additional_price
                      }
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
                      <option value="Y">
                        활성
                      </option>

                      <option value="N">
                        비활성
                      </option>
                    </select>
                  </label>

                  <button
                    type="button"
                    onClick={() =>
                      handleVariantSave(
                        variant,
                      )
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
                      handleVariantDelete(
                        variant,
                      )
                    }
                    disabled={
                      deletingVariantId ===
                        variant.variant_id ||
                      variant.active_yn ===
                        "N"
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
                inventoryDrafts[
                  item.inventory_id
                ] || {
                  stock_quantity:
                    item.stock_quantity,
                  safety_stock:
                    item.safety_stock,
                };

              return (
                <div
                  key={item.inventory_id}
                >
                  <p>{item.org_name}</p>

                  <p>
                    SKU: {item.variant_id}
                  </p>

                  <label>
                    재고 수량
                    <input
                      type="number"
                      min="0"
                      value={
                        draft.stock_quantity
                      }
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
                      value={
                        draft.safety_stock
                      }
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
                    예약:{" "}
                    {item.reserved_quantity}
                  </p>

                  <p>
                    현재 판매 가능 수량:{" "}
                    {item.available_quantity}
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      handleInventorySave(
                        item,
                      )
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

      <div>
        <h2>상품 매뉴얼 / 첨부파일</h2>

        {productFiles.length === 0 ? (
          <p className="product-state">
            등록된 상품 매뉴얼 또는 첨부파일이 없습니다.
          </p>
        ) : (
          <div>
            {productFiles.map((file) => (
              <div
                key={`${file.product_id}-${file.file_id}`}
                style={{
                  padding: "12px 0",
                  borderBottom: "1px solid #ddd",
                }}
              >
                <p>
                  <strong>
                    {file.file_description ||
                      file.original_file_name}
                  </strong>
                </p>

                <p>
                  파일 구분: {file.file_category}
                </p>

                <p>
                  파일명: {file.original_file_name}
                </p>

                {file.public_url ? (
                  <a
                    href={file.public_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    파일 열기
                  </a>
                ) : (
                  <p className="product-state">
                    연결된 파일 URL이 없습니다.
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <ProductImageManager productId={productId} />
    </section>
  );
}