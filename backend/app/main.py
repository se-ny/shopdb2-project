
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers.carts import router as carts_router

from app.core.database import check_database_connection


from app.routers.products import router as products_router
from app.routers.orders import router as orders_router


from app.routers.seller_products import router as seller_products_router
from app.routers.seller_orders import router as seller_orders_router
from app.routers.seller_profiles import router as seller_profiles_router
from app.routers.payments import router as payments_router

from app.routers import org_units, users, roles, policies, ai_providers, rag_documents, rag_query, auth
from app.routers import admin_payments
from app.routers import admin_payments, admin_logs
from app.routers import admin_alerts
from app.routers import ai_feedback
from app.routers import admin_sql_agent
from app.routers import admin_orders
from app.routers import admin_dashboard
from app.routers import admin_products
from app.routers import admin_categories


from app.routers import (
    ai_providers,
    org_units,
    policies,
    rag_documents,
    rag_query,
    roles,
    users,
)


app = FastAPI(
    title="SHOPDB2 API",
    description="SHOPDB2 공통 FastAPI 백엔드",
    version="0.1.0",
)


app.include_router(products_router)
app.include_router(carts_router)
app.include_router(orders_router)


app.include_router(seller_products_router)
app.include_router(seller_orders_router)
app.include_router(seller_profiles_router)
app.include_router(payments_router)


app.include_router(org_units.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(policies.router)
app.include_router(ai_providers.router)
app.include_router(rag_documents.router)
app.include_router(rag_query.router)
app.include_router(admin_payments.router)
app.include_router(admin_logs.router)
app.include_router(admin_alerts.router)
app.include_router(ai_feedback.router)
app.include_router(admin_sql_agent.router)
app.include_router(auth.router)
app.include_router(admin_orders.router)
app.include_router(admin_dashboard.router)
app.include_router(admin_products.router)
app.include_router(admin_categories.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """백엔드 기본 실행 상태를 확인합니다."""

    return {
        "success": True,
        "message": "SHOPDB2 API가 정상적으로 실행 중입니다.",
    }


@app.get("/api/health")
def health_check():
    """Frontend와 Backend의 연결 상태를 확인합니다."""

    return {
        "success": True,
        "status": "healthy",
    }


@app.get("/api/health/db")
def database_health_check():
    """FastAPI와 MySQL shopdb2의 연결 상태를 확인합니다."""

    try:
        result = check_database_connection()

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="MySQL 데이터베이스 연결에 실패했습니다.",
        ) from error

    return {
        "success": True,
        "status": "connected",
        **result,
    }