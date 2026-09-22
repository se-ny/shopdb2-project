import { useState } from "react";
import { createCategory, updateCategory } from "../../api/admin";

function CategoryForm({ categories, editingCategory, onSaved, onCancel }) {
  const isEdit = !!editingCategory;

  const [form, setForm] = useState({
    category_name: editingCategory?.category_name ?? "",
    parent_category_id: editingCategory?.parent_category_id ?? "",
    display_order: editingCategory?.display_order ?? 0,
  });
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function handleChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setErrorMessage("");
    try {
      const payload = {
        category_name: form.category_name,
        parent_category_id: form.parent_category_id ? Number(form.parent_category_id) : null,
        display_order: Number(form.display_order),
      };
      if (isEdit) {
        await updateCategory(editingCategory.category_id, payload);
      } else {
        await createCategory(payload);
      }
      onSaved();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="admin-form">
      <h2>{isEdit ? "카테고리 수정" : "카테고리 등록"}</h2>
      <label>
        카테고리명
        <input value={form.category_name} onChange={(e) => handleChange("category_name", e.target.value)} required />
      </label>
      <label>
        상위 카테고리 (비워두면 최상위)
        <select
          value={form.parent_category_id}
          onChange={(e) => handleChange("parent_category_id", e.target.value)}
        >
          <option value="">(최상위)</option>
          {categories
            .filter((c) => !editingCategory || c.category_id !== editingCategory.category_id)
            .map((c) => (
              <option key={c.category_id} value={c.category_id}>
                {"　".repeat(c.category_level - 1)}{c.category_name}
              </option>
            ))}
        </select>
      </label>
      <label>
        정렬순서
        <input type="number" value={form.display_order} onChange={(e) => handleChange("display_order", e.target.value)} />
      </label>

      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="admin-form-actions">
        <button type="submit" disabled={saving}>{saving ? "저장 중..." : isEdit ? "수정 저장" : "등록"}</button>
        <button type="button" onClick={onCancel} disabled={saving}>취소</button>
      </div>
    </form>
  );
}

export default CategoryForm;