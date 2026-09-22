import { useEffect, useState } from "react";
import { fetchCategories, deactivateCategory } from "../../api/admin";
import CategoryForm from "./CategoryForm";

function CategoryList() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);

  function loadCategories() {
    setLoading(true);
    fetchCategories()
      .then(setCategories)
      .catch((error) => setErrorMessage(error.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadCategories();
  }, []);

  function handleAddClick() {
    setEditingCategory(null);
    setShowForm(true);
  }

  function handleEditClick(category) {
    setEditingCategory(category);
    setShowForm(true);
  }

  function handleSaved() {
    setShowForm(false);
    setEditingCategory(null);
    loadCategories();
  }

  async function handleDeactivate(category) {
    if (!confirm(`"${category.category_name}"을(를) 비활성화하시겠습니까?`)) return;
    try {
      await deactivateCategory(category.category_id);
      loadCategories();
    } catch (error) {
      alert(`처리 실패: ${error.message}`);
    }
  }

  if (loading) return <p>불러오는 중...</p>;
  if (errorMessage) return <p className="error-message">{errorMessage}</p>;

  return (
    <div>
      <div className="admin-page-header">
        <h1>카테고리관리</h1>
        {!showForm && <button onClick={handleAddClick}>+ 카테고리 등록</button>}
      </div>

      {showForm && (
        <CategoryForm
          categories={categories}
          editingCategory={editingCategory}
          onSaved={handleSaved}
          onCancel={() => setShowForm(false)}
        />
      )}

      <table className="admin-table">
        <thead>
          <tr>
            <th>카테고리명</th>
            <th>레벨</th>
            <th>정렬순서</th>
            <th>상태</th>
            <th>동작</th>
          </tr>
        </thead>
        <tbody>
          {categories.map((c) => (
            <tr key={c.category_id}>
              <td>{"　".repeat(c.category_level - 1)}{c.category_name}</td>
              <td>{c.category_level}</td>
              <td>{c.display_order}</td>
              <td>{c.active_yn === "Y" ? "활성" : "비활성"}</td>
              <td>
                <button onClick={() => handleEditClick(c)}>수정</button>
                {c.active_yn === "Y" && (
                  <button onClick={() => handleDeactivate(c)}>비활성화</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default CategoryList;