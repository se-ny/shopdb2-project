import { useEffect, useState } from "react";
import {
  getSellerOrderDetail,
  getSellerOrders,
} from "../../api/sellerOrders";

function formatPrice(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return `${number.toLocaleString("ko-KR")}원`;
}

export default function SellerOrderList() {
  const [sellerUserId, setSellerUserId] = useState(2);

  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] =
    useState(null);

  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] =
    useState(false);

  const [error, setError] = useState("");

  async function loadOrders() {
    try {
      setLoading(true);
      setError("");
      setSelectedOrder(null);

      const data = await getSellerOrders(
        sellerUserId,
      );

      setOrders(data);
    } catch (err) {
      setError(
        err.message ||
          "판매 주문을 불러오지 못했습니다.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadOrders();
  }, [sellerUserId]);

  async function handleOrderClick(orderId) {
    try {
      setDetailLoading(true);
      setError("");

      const data =
        await getSellerOrderDetail(
          orderId,
          sellerUserId,
        );

      setSelectedOrder(data);
    } catch (err) {
      setError(
        err.message ||
          "주문 상세 정보를 불러오지 못했습니다.",
      );
    } finally {
      setDetailLoading(false);
    }
  }

  return (
    <section
      style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "24px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <div>
          <p>SHOPDB2 SELLER</p>
          <h1>판매 주문 관리</h1>
        </div>

        <label>
          판매자
          <select
            value={sellerUserId}
            onChange={(event) =>
              setSellerUserId(
                Number(event.target.value),
              )
            }
            style={{
              marginLeft: "8px",
              padding: "8px",
            }}
          >
            <option value={2}>
              전자판매자
            </option>

            <option value={3}>
              패션판매자
            </option>
          </select>
        </label>
      </div>

      {error && (
        <p
          style={{
            color: "red",
          }}
        >
          {error}
        </p>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1fr) minmax(0, 1fr)",
          gap: "24px",
        }}
      >
        <div>
          <h2>주문 목록</h2>

          {loading ? (
            <p>주문을 불러오는 중입니다.</p>
          ) : orders.length === 0 ? (
            <p>판매 주문이 없습니다.</p>
          ) : (
            <div
              style={{
                display: "grid",
                gap: "12px",
              }}
            >
              {orders.map((order) => (
                <button
                  key={order.order_id}
                  type="button"
                  onClick={() =>
                    handleOrderClick(
                      order.order_id,
                    )
                  }
                  style={{
                    textAlign: "left",
                    padding: "16px",
                    border:
                      "1px solid #dddddd",
                    borderRadius: "10px",
                    background: "#ffffff",
                    cursor: "pointer",
                  }}
                >
                  <strong>
                    {order.order_no}
                  </strong>

                  <p>
                    상태:{" "}
                    {order.order_status}
                  </p>

                  <p>
                    구매자 ID:{" "}
                    {order.buyer_user_id}
                  </p>

                  <p>
                    주문금액:{" "}
                    {formatPrice(
                      order.total_amount,
                    )}
                  </p>

                  <p>
                    주문일:{" "}
                    {order.ordered_at || "-"}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        <div>
          <h2>주문 상세</h2>

          {detailLoading ? (
            <p>
              주문 상세 정보를 불러오는
              중입니다.
            </p>
          ) : !selectedOrder ? (
            <p>
              왼쪽 주문을 선택하세요.
            </p>
          ) : (
            <div
              style={{
                padding: "20px",
                border:
                  "1px solid #dddddd",
                borderRadius: "10px",
              }}
            >
              <p>
                주문번호:{" "}
                {selectedOrder.order_no}
              </p>

              <p>
                주문상태:{" "}
                {selectedOrder.order_status}
              </p>

              <p>
                구매자 ID:{" "}
                {
                  selectedOrder.buyer_user_id
                }
              </p>

              <p>
                상품금액:{" "}
                {formatPrice(
                  selectedOrder.product_amount,
                )}
              </p>

              <p>
                할인금액:{" "}
                {formatPrice(
                  selectedOrder.discount_amount,
                )}
              </p>

              <p>
                배송비:{" "}
                {formatPrice(
                  selectedOrder.shipping_amount,
                )}
              </p>

              <p>
                총 결제금액:{" "}
                {formatPrice(
                  selectedOrder.total_amount,
                )}
              </p>

              <h3>판매 상품</h3>

              {selectedOrder.items.length ===
              0 ? (
                <p>
                  해당 판매자의 주문 상품이
                  없습니다.
                </p>
              ) : (
                selectedOrder.items.map(
                  (item) => (
                    <div
                      key={
                        item.order_item_id
                      }
                      style={{
                        marginTop: "12px",
                        padding: "12px",
                        border:
                          "1px solid #eeeeee",
                        borderRadius: "8px",
                      }}
                    >
                      <strong>
                        {
                          item.product_name_snapshot
                        }
                      </strong>

                      <p>
                        SKU:{" "}
                        {item.sku_snapshot ||
                          "-"}
                      </p>

                      <p>
                        수량:{" "}
                        {item.quantity}
                      </p>

                      <p>
                        단가:{" "}
                        {formatPrice(
                          item.unit_price,
                        )}
                      </p>

                      <p>
                        상품금액:{" "}
                        {formatPrice(
                          item.item_amount,
                        )}
                      </p>

                      <p>
                        상태:{" "}
                        {item.item_status}
                      </p>
                    </div>
                  ),
                )
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}