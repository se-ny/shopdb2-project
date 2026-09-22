const SELLER_MENUS = [
  {
    key: "seller-products",
    title: "상품 관리",
    description:
      "판매 상품 목록을 확인하고 상품 상세, 옵션, 재고, 이미지를 관리합니다.",
  },
  {
    key: "seller-orders",
    title: "판매 주문 관리",
    description:
      "판매 상품이 포함된 주문 목록과 주문 상세 정보를 확인합니다.",
  },
  {
    key: "seller-profile",
    title: "판매자 정보 관리",
    description:
      "판매자 회사 정보와 정산 정보, 판매 상태를 확인하고 수정합니다.",
  },
  {
    key: "seller-product-new",
    title: "상품 등록",
    description:
      "새로운 판매 상품의 기본 정보를 등록합니다.",
  },
];

export default function SellerDashboard({
  onBack,
  onSelect,
}) {
  return (
    <section
      style={{
        width: "min(1120px, calc(100% - 48px))",
        margin: "0 auto",
        padding: "32px 0 72px",
      }}
    >
      <button
        type="button"
        onClick={onBack}
        style={{
          marginBottom: "28px",
          padding: "9px 14px",
          border: "1px solid #d7dce5",
          borderRadius: "7px",
          background: "#ffffff",
          cursor: "pointer",
        }}
      >
        ← SHOPDB2 소개
      </button>

      <p
        style={{
          margin: "0 0 8px",
          fontSize: "12px",
          fontWeight: 700,
          letterSpacing: "0.08em",
        }}
      >
        SHOPDB2 SELLER
      </p>

      <h1
        style={{
          margin: "0 0 10px",
          fontSize: "34px",
          color: "#081f55",
        }}
      >
        판매자 운영
      </h1>

      <p
        style={{
          margin: "0 0 32px",
          color: "#566174",
          lineHeight: 1.7,
        }}
      >
        사용할 판매자 기능을 선택해서 각 관리 화면으로 이동합니다.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(230px, 1fr))",
          gap: "18px",
        }}
      >
        {SELLER_MENUS.map((menu) => (
          <article
            key={menu.key}
            style={{
              display: "flex",
              minHeight: "190px",
              flexDirection: "column",
              padding: "24px",
              border: "1px solid #dce3ed",
              borderRadius: "12px",
              background: "#ffffff",
            }}
          >
            <h2
              style={{
                margin: "0 0 12px",
                fontSize: "21px",
                color: "#081f55",
              }}
            >
              {menu.title}
            </h2>

            <p
              style={{
                flex: 1,
                margin: "0 0 22px",
                color: "#566174",
                lineHeight: 1.65,
              }}
            >
              {menu.description}
            </p>

            <button
              type="button"
              onClick={() => onSelect(menu.key)}
              style={{
                alignSelf: "flex-start",
                padding: "10px 15px",
                border: 0,
                borderRadius: "7px",
                background: "#071529",
                color: "#ffffff",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              {menu.title} 들어가기
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
