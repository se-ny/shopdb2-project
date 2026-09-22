import { useEffect, useState } from "react";
import {
  createProductImage,
  deleteProductImage,
  getProductImages,
  updateProductImage,
} from "../api/products";

const EMPTY_IMAGE = {
  public_url: "",
  thumbnail_url: "",
  original_file_name: "",
  image_type: "DETAIL",
  alt_text: "",
  display_order: 0,
};

export default function ProductImageManager({
  productId,
}) {
  const [images, setImages] = useState([]);
  const [newImage, setNewImage] =
    useState(EMPTY_IMAGE);

  const [drafts, setDrafts] = useState({});

  const [loading, setLoading] = useState(true);
  const [creating, setCreating] =
    useState(false);

  const [savingId, setSavingId] =
    useState(null);

  const [deletingId, setDeletingId] =
    useState(null);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadImages() {
    try {
      setLoading(true);
      setError("");

      const data =
        await getProductImages(productId);

      setImages(data);

      const draftData = {};

      data.forEach((image) => {
        draftData[image.product_image_id] = {
          public_url:
            image.public_url || "",
          thumbnail_url:
            image.thumbnail_url || "",
          image_type:
            image.image_type || "DETAIL",
          alt_text:
            image.alt_text || "",
          display_order:
            image.display_order ?? 0,
          active_yn:
            image.active_yn || "Y",
        };
      });

      setDrafts(draftData);
    } catch (err) {
      setError(
        err.message ||
          "상품 이미지를 불러오지 못했습니다.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (productId) {
      loadImages();
    }
  }, [productId]);

  function handleNewImageChange(event) {
    const { name, value } = event.target;

    setNewImage((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function handleDraftChange(
    imageId,
    field,
    value,
  ) {
    setDrafts((current) => ({
      ...current,
      [imageId]: {
        ...current[imageId],
        [field]: value,
      },
    }));
  }

  async function handleCreate(event) {
    event.preventDefault();

    if (!newImage.public_url.trim()) {
      setError("이미지 URL을 입력해주세요.");
      return;
    }

    try {
      setCreating(true);
      setError("");
      setMessage("");

      await createProductImage(productId, {
        public_url:
          newImage.public_url.trim(),

        thumbnail_url:
          newImage.thumbnail_url.trim() ||
          null,

        original_file_name:
          newImage.original_file_name.trim() ||
          null,

        image_type:
          newImage.image_type,

        alt_text:
          newImage.alt_text.trim() || null,

        display_order: Number(
          newImage.display_order,
        ),
      });

      setNewImage(EMPTY_IMAGE);

      await loadImages();

      setMessage(
        "상품 이미지가 등록되었습니다.",
      );
    } catch (err) {
      setError(
        err.message ||
          "상품 이미지 등록에 실패했습니다.",
      );
    } finally {
      setCreating(false);
    }
  }

  async function handleUpdate(imageId) {
    const draft = drafts[imageId];

    if (!draft.public_url.trim()) {
      setError("이미지 URL을 입력해주세요.");
      return;
    }

    try {
      setSavingId(imageId);
      setError("");
      setMessage("");

      await updateProductImage(
        productId,
        imageId,
        {
          public_url:
            draft.public_url.trim(),

          thumbnail_url:
            draft.thumbnail_url.trim() ||
            null,

          image_type:
            draft.image_type,

          alt_text:
            draft.alt_text.trim() || null,

          display_order: Number(
            draft.display_order,
          ),

          active_yn:
            draft.active_yn,
        },
      );

      await loadImages();

      setMessage(
        "상품 이미지가 수정되었습니다.",
      );
    } catch (err) {
      setError(
        err.message ||
          "상품 이미지 수정에 실패했습니다.",
      );
    } finally {
      setSavingId(null);
    }
  }

  async function handleDelete(imageId) {
    const confirmed = window.confirm(
      "이 상품 이미지를 삭제 처리하시겠습니까?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(imageId);
      setError("");
      setMessage("");

      await deleteProductImage(
        productId,
        imageId,
      );

      await loadImages();

      setMessage(
        "상품 이미지가 삭제 처리되었습니다.",
      );
    } catch (err) {
      setError(
        err.message ||
          "상품 이미지 삭제에 실패했습니다.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section
      style={{
        marginTop: "32px",
      }}
    >
      <h2>상품 이미지 관리</h2>

      {error && (
        <p
          style={{
            color: "red",
          }}
        >
          {error}
        </p>
      )}

      {message && (
        <p>{message}</p>
      )}

      <form
        onSubmit={handleCreate}
        style={{
          display: "grid",
          gap: "10px",
          padding: "20px",
          marginBottom: "24px",
          border: "1px solid #dddddd",
          borderRadius: "10px",
        }}
      >
        <h3>신규 이미지 등록</h3>

        <label>
          이미지 URL
          <input
            type="text"
            name="public_url"
            value={newImage.public_url}
            onChange={handleNewImageChange}
            placeholder="https://example.com/image.jpg"
          />
        </label>

        <label>
          썸네일 URL
          <input
            type="text"
            name="thumbnail_url"
            value={
              newImage.thumbnail_url
            }
            onChange={handleNewImageChange}
            placeholder="선택 입력"
          />
        </label>

        <label>
          원본 파일명
          <input
            type="text"
            name="original_file_name"
            value={
              newImage.original_file_name
            }
            onChange={handleNewImageChange}
            placeholder="예: notebook.jpg"
          />
        </label>

        <label>
          이미지 종류
          <select
            name="image_type"
            value={newImage.image_type}
            onChange={handleNewImageChange}
          >
            <option value="MAIN">
              대표 이미지
            </option>

            <option value="DETAIL">
              상세 이미지
            </option>

            <option value="THUMBNAIL">
              썸네일
            </option>

            <option value="OPTION">
              옵션 이미지
            </option>
          </select>
        </label>

        <label>
          이미지 설명
          <input
            type="text"
            name="alt_text"
            value={newImage.alt_text}
            onChange={handleNewImageChange}
            placeholder="예: 노트북 정면 이미지"
          />
        </label>

        <label>
          표시 순서
          <input
            type="number"
            name="display_order"
            min="0"
            value={
              newImage.display_order
            }
            onChange={handleNewImageChange}
          />
        </label>

        <button
          type="submit"
          disabled={creating}
        >
          {creating
            ? "등록 중..."
            : "+ 이미지 등록"}
        </button>
      </form>

      <h3>등록된 이미지</h3>

      {loading ? (
        <p>이미지를 불러오는 중입니다.</p>
      ) : images.length === 0 ? (
        <p>등록된 이미지가 없습니다.</p>
      ) : (
        <div
          style={{
            display: "grid",
            gap: "20px",
          }}
        >
          {images.map((image) => {
            const draft =
              drafts[
                image.product_image_id
              ];

            if (!draft) {
              return null;
            }

            return (
              <article
                key={
                  image.product_image_id
                }
                style={{
                  padding: "20px",
                  border:
                    "1px solid #dddddd",
                  borderRadius: "10px",
                }}
              >
                {image.public_url && (
                  <img
                    src={image.public_url}
                    alt={
                      image.alt_text ||
                      "상품 이미지"
                    }
                    style={{
                      width: "200px",
                      height: "160px",
                      objectFit: "contain",
                      marginBottom: "16px",
                    }}
                    onError={(event) => {
                      event.currentTarget.style.display =
                        "none";
                    }}
                  />
                )}

                <p>
                  이미지 ID:{" "}
                  {image.product_image_id}
                </p>

                <p>
                  File ID: {image.file_id}
                </p>

                <label>
                  이미지 URL
                  <input
                    type="text"
                    value={draft.public_url}
                    onChange={(event) =>
                      handleDraftChange(
                        image.product_image_id,
                        "public_url",
                        event.target.value,
                      )
                    }
                  />
                </label>

                <label>
                  썸네일 URL
                  <input
                    type="text"
                    value={
                      draft.thumbnail_url
                    }
                    onChange={(event) =>
                      handleDraftChange(
                        image.product_image_id,
                        "thumbnail_url",
                        event.target.value,
                      )
                    }
                  />
                </label>

                <label>
                  이미지 종류
                  <select
                    value={draft.image_type}
                    onChange={(event) =>
                      handleDraftChange(
                        image.product_image_id,
                        "image_type",
                        event.target.value,
                      )
                    }
                  >
                    <option value="MAIN">
                      대표 이미지
                    </option>

                    <option value="DETAIL">
                      상세 이미지
                    </option>

                    <option value="THUMBNAIL">
                      썸네일
                    </option>

                    <option value="OPTION">
                      옵션 이미지
                    </option>
                  </select>
                </label>

                <label>
                  이미지 설명
                  <input
                    type="text"
                    value={draft.alt_text}
                    onChange={(event) =>
                      handleDraftChange(
                        image.product_image_id,
                        "alt_text",
                        event.target.value,
                      )
                    }
                  />
                </label>

                <label>
                  표시 순서
                  <input
                    type="number"
                    min="0"
                    value={
                      draft.display_order
                    }
                    onChange={(event) =>
                      handleDraftChange(
                        image.product_image_id,
                        "display_order",
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
                      handleDraftChange(
                        image.product_image_id,
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

                <div
                  style={{
                    display: "flex",
                    gap: "10px",
                    marginTop: "14px",
                  }}
                >
                  <button
                    type="button"
                    onClick={() =>
                      handleUpdate(
                        image.product_image_id,
                      )
                    }
                    disabled={
                      savingId ===
                      image.product_image_id
                    }
                  >
                    {savingId ===
                    image.product_image_id
                      ? "저장 중..."
                      : "이미지 저장"}
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      handleDelete(
                        image.product_image_id,
                      )
                    }
                    disabled={
                      deletingId ===
                        image.product_image_id ||
                      image.active_yn === "N"
                    }
                  >
                    {deletingId ===
                    image.product_image_id
                      ? "삭제 중..."
                      : "이미지 삭제"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}