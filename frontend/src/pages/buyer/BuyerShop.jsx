import { useEffect, useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import BuyerProductList from "./BuyerProductList";
import BuyerProductDetail from "./BuyerProductDetail";
import BuyerCart from "./BuyerCart";
import BuyerCheckout from "./BuyerCheckout";
import BuyerOrders from "./BuyerOrders";
import "../../styles/buyer.css";

export default function BuyerShop() {
  const { auth } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const restored = location.state?.buyerReturn || null;

  const [view, setView] = useState(restored?.view || "products");
  const [productId, setProductId] = useState(
    restored?.productId ?? null,
  );
  const [checkoutItems, setCheckoutItems] = useState([]);
  const [createdOrder, setCreatedOrder] = useState(null);

  useEffect(() => {
    if (restored) {
      navigate(location.pathname, {
        replace: true,
        state: null,
      });
    }
  }, []);

  function go(viewName) {
    setView(viewName);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function requireLogin(targetView = view) {
    if (auth) return true;

    navigate("/login", {
      state: {
        buyerReturn: {
          view: targetView,
          productId,
        },
      },
    });

    return false;
  }

  function openProducts() {
    setProductId(null);
    setCheckoutItems([]);
    go("products");
  }

  function openProduct(id) {
    setProductId(id);
    go("product-detail");
  }

  function openCart() {
    if (!requireLogin("cart")) return;
    setCheckoutItems([]);
    go("cart");
  }

  function openOrders() {
    if (!requireLogin("orders")) return;
    go("orders");
  }

  function startCartCheckout(items) {
    if (!requireLogin("cart")) return;
    setCheckoutItems(items);
    go("checkout");
  }

  function startBuyNow(item) {
    if (!requireLogin("product-detail")) return;

    // 바로구매는 cart_item_id를 만들거나 전달하지 않는다.
    setCheckoutItems([item]);
    go("checkout");
  }

  function handleOrderCreated(order) {
    setCreatedOrder(order);
    go("order-created");
  }

  return (
    <div className="buyer-shell">
      <header className="buyer-topbar">
        <button
          type="button"
          className="buyer-brand"
          onClick={openProducts}
        >
          SHOPDB2
        </button>

        <nav className="buyer-nav" aria-label="구매자 메뉴">
          <button
            type="button"
            className={
              view === "products" || view === "product-detail"
                ? "is-active"
                : ""
            }
            onClick={openProducts}
          >
            상품
          </button>

          <button
            type="button"
            className={view === "cart" ? "is-active" : ""}
            onClick={openCart}
          >
            장바구니
          </button>

          <button
            type="button"
            className={view === "orders" ? "is-active" : ""}
            onClick={openOrders}
          >
            주문내역
          </button>
        </nav>
      </header>

      <main>
        {view === "products" && (
          <BuyerProductList onSelect={openProduct} />
        )}

        {view === "product-detail" && productId !== null && (
          <BuyerProductDetail
            productId={productId}
            onBack={openProducts}
            onCart={openCart}
            onBuyNow={startBuyNow}
            isAuthenticated={Boolean(auth)}
            onRequireLogin={() => requireLogin("product-detail")}
          />
        )}

        {view === "cart" && auth && (
          <BuyerCart onCheckout={startCartCheckout} />
        )}

        {view === "checkout" && auth && (
          <BuyerCheckout
            items={checkoutItems}
            onCreated={handleOrderCreated}
            onBack={
              checkoutItems.some((item) => item.cart_item_id)
                ? openCart
                : () =>
                    productId !== null
                      ? openProduct(productId)
                      : openProducts()
            }
          />
        )}

        {view === "orders" && auth && <BuyerOrders />}

        {view === "order-created" && createdOrder && auth && (
          <section className="buyer-page">
            <div className="buyer-result-card">
              <div className="buyer-result-icon">✓</div>

              <p className="buyer-eyebrow">ORDER CREATED</p>

              <h1>주문이 생성되었습니다.</h1>

              <p>
                주문번호 <strong>{createdOrder.order_no}</strong>
              </p>

              <div className="buyer-alert buyer-alert--warning">
                주문은 생성되었지만 아직 결제가 완료된 것은 아닙니다.
                다음 단계에서 결제를 진행해야 합니다.
              </div>

              <div className="buyer-result-actions">
                <button
                  type="button"
                  className="buyer-primary-button"
                  onClick={openOrders}
                >
                  주문내역 확인
                </button>

                <button
                  type="button"
                  className="buyer-secondary-button"
                  onClick={openProducts}
                >
                  쇼핑 계속하기
                </button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
