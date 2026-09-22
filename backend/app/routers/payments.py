from typing import Generator, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import engine
from app.core.deps import CurrentUser, require_role
from app.schemas.payment import (
    PaymentCreate,
    PaymentOut,
    PaymentTransactionCreate,
    PaymentTransactionOut,
    PaymentUpdate,
    PaymentWebhookCreate,
    PaymentWebhookOut,
)
from app.services import payment_service
from app.services.payment_service import (
    PaymentNotFoundError,
    PaymentValidationError,
)


router = APIRouter(
    prefix="/api/payments",
    tags=["결제관리"],
)


def get_db() -> Generator[Session, None, None]:
    db = Session(engine)

    try:
        yield db
    finally:
        db.close()


def _handle_payment_error(exc: Exception):
    if isinstance(exc, PaymentNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(exc, PaymentValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    raise exc


# =========================================================
# Payment
# =========================================================

@router.post(
    "",
    response_model=PaymentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("BUYER")),
):
    try:
        return payment_service.create_payment(
            db,
            payload,
            current_user.user_id,
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)


@router.get(
    "/order/{order_id}",
    response_model=list[PaymentOut],
)
def get_payments_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("BUYER")),
):
    try:
        return payment_service.get_payments_by_order(
            db,
            order_id,
            current_user.user_id,
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)


@router.get(
    "/{payment_id}",
    response_model=PaymentOut,
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("BUYER")),
):
    try:
        return payment_service.get_payment(
            db,
            payment_id,
            current_user.user_id,
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)


@router.put(
    "/{payment_id}",
    response_model=PaymentOut,
)
def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    current_user: CurrentUser = Depends(require_role("BUYER")),
    db: Session = Depends(get_db),
):
    try:
        return payment_service.update_payment(
            db,
            payment_id,
            payload,

            buyer_user_id=current_user.user_id,
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)


# =========================================================
# Transaction
# =========================================================

@router.post(
    "/{payment_id}/transactions",
    response_model=PaymentTransactionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_transaction(
    payment_id: int,
    payload: PaymentTransactionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("BUYER")),
):
    try:
        return (
            payment_service
            .create_payment_transaction(
                db,
                payment_id,
                payload,
                current_user.user_id,
            )
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)


@router.get(
    "/{payment_id}/transactions",
    response_model=list[PaymentTransactionOut],
)
def get_payment_transactions(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("BUYER")),
):
    try:
        return (
            payment_service
            .get_payment_transactions(
                db,
                payment_id,
                current_user.user_id,
            )
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)


# =========================================================
# Webhook
# =========================================================

@router.post(
    "/webhooks/events",
    response_model=PaymentWebhookOut,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_webhook(
    payload: PaymentWebhookCreate,
    db: Session = Depends(get_db),
):
    try:
        return (
            payment_service
            .create_payment_webhook(
                db,
                payload,
            )
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)


@router.patch(
    "/webhooks/{webhook_id}/processed",
    response_model=PaymentWebhookOut,
)
def mark_webhook_processed(
    webhook_id: int,
    success: bool = Query(...),
    error_message: Optional[str] = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    try:
        return (
            payment_service
            .mark_webhook_processed(
                db,
                webhook_id,
                success,
                error_message,
            )
        )

    except (
        PaymentNotFoundError,
        PaymentValidationError,
    ) as exc:
        _handle_payment_error(exc)
