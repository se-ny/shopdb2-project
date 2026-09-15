from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import check_database_connection
from app.routers.products import router as products_router

app = FastAPI(
    title="SHOPDB2 API",
    description="SHOPDB2 공통 FastAPI 백엔드",
    version="0.1.0",
)

app.include_router(products_router)


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