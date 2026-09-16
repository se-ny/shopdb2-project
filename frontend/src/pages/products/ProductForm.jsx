
import { useState } from "react";
import { createProduct } from "../../api/products";

const CATEGORY_OPTIONS = [
  { id: 1, name: "전자제품" },
  { id: 2, name: "패션" },
  { id: 3, name: "노트북" },
  { id: 4, name: "스마트폰" },
  { id: 5, name: "상의" },
  { id: 6, name: "신발" },
];

const INITIAL_FORM = {
  seller_user_id: 2,
  category_id: 3,
  product_code: "",
  product_name: "",
  short_description: "",
  description: "",
  regular_price: "",
  sale_price: "",
  product_status: "READY",
};

export default function ProductForm({
  onCreated,
  onCancel,
}) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    if (!form.product_code.trim()) {
      setError("상품코드를 입력해주세요.");
      return;
    }

    if (!form.product_name.trim()) {
      setError("상품명을 입력해주세요.");
      return;
    }

    const regularPrice = Number(form.regular_price);
    const salePrice = Number(form.sale_price);

    if (regularPrice <= 0 || salePrice <= 0) {
      setError("상품 가격은 0보다 커야 합니다.");
      return;
    }

    if (salePrice > regularPrice) {
      setError(
        "판매가는 정상가보다 높게 설정할 수 없습니다.",
      );
      return;
    }

    try {
      setSaving(true);

      const created = await createProduct({
        seller_user_id: Number(form.seller_user_id),
        category_id: Number(form.category_id),

        product_code: form.product_code.trim(),
        product_name: form.product_name.trim(),

        short_description:
          form.short_description.trim() || null,

        description:
          form.description.trim() || null,

        regular_price: regularPrice,
        sale_price: salePrice,

        product_status: form.product_status,
      });

      if (onCreated) {
        onCreated(created);
      }
    } catch (err) {
      setError(
        err.message || "상품 등록에 실패했습니다.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="product-page">
      <div className="product-page__header">
        <div>
          <p className="product-page__eyebrow">
            SHOPDB2 SELLER
          </p>

          <h1>상품 등록</h1>

          <p>
            판매할 상품의 기본 정보를 입력합니다.
          </p>
        </div>
      </div>

      {error && (
        <p className="product-state product-state--error">
          {error}
        </p>
      )}

      <form
        onSubmit={handleSubmit}
        style={{
          display: "grid",
          gap: "18px",
          maxWidth: "800px",
          padding: "24px",
          border: "1px solid #eeeeee",
          borderRadius: "14px",
          background: "#ffffff",
        }}
      >
        <label>
          판매자

          <select
            name="seller_user_id"
            value={form.seller_user_id}
            onChange={handleChange}
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
            }}
          >
            <option value="2">
              전자판매자 (user_id 2)
            </option>

            <option value="3">
              패션판매자 (user_id 3)
            </option>
          </select>
        </label>

        <label>
          카테고리

          <select
            name="category_id"
            value={form.category_id}
            onChange={handleChange}
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
            }}
          >
            {CATEGORY_OPTIONS.map((category) => (
              <option
                key={category.id}
                value={category.id}
              >
                {category.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          상품코드

          <input
            type="text"
            name="product_code"
            value={form.product_code}
            onChange={handleChange}
            placeholder="예: NOTEBOOK-NEW-001"
            maxLength={50}
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <label>
          상품명

          <input
            type="text"
            name="product_name"
            value={form.product_name}
            onChange={handleChange}
            placeholder="상품명을 입력하세요."
            maxLength={200}
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <label>
          짧은 설명

          <input
            type="text"
            name="short_description"
            value={form.short_description}
            onChange={handleChange}
            placeholder="상품 목록 등에 표시할 설명"
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <label>
          상세 설명

          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            rows={6}
            placeholder="상품 상세 설명"
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
              boxSizing: "border-box",
              resize: "vertical",
            }}
          />
        </label>

        <label>
          정상가

          <input
            type="number"
            name="regular_price"
            value={form.regular_price}
            onChange={handleChange}
            min="1"
            placeholder="예: 1500000"
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <label>
          판매가

          <input
            type="number"
            name="sale_price"
            value={form.sale_price}
            onChange={handleChange}
            min="1"
            placeholder="예: 1390000"
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
              boxSizing: "border-box",
            }}
          />
        </label>

        <label>
          상품 상태

          <select
            name="product_status"
            value={form.product_status}
            onChange={handleChange}
            style={{
              display: "block",
              width: "100%",
              marginTop: "6px",
              padding: "10px",
            }}
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
          </select>
        </label>

        <div
          style={{
            display: "flex",
            gap: "10px",
          }}
        >
          <button
            type="submit"
            disabled={saving}
            style={{
              padding: "12px 20px",
              border: "0",
              borderRadius: "8px",
              background: "#111111",
              color: "#ffffff",
              cursor: "pointer",
            }}
          >
            {saving
              ? "상품 등록 중..."
              : "상품 등록"}
          </button>

          <button
            type="button"
            onClick={onCancel}
            disabled={saving}
            style={{
              padding: "12px 20px",
              border: "1px solid #dddddd",
              borderRadius: "8px",
              background: "#ffffff",
              cursor: "pointer",
            }}
          >
            취소
          </button>
        </div>
      </form>
    </section>
  );
}