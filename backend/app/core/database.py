from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from app.core.config import settings


database_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
    query={"charset": "utf8mb4"},
)


engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)


def check_database_connection() -> dict:
    """현재 DB 이름과 기본 테이블 개수를 조회합니다."""

    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT DATABASE()")
        ).scalar_one()

        table_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = :db_name
                  AND table_type = 'BASE TABLE'
                """
            ),
            {"db_name": settings.db_name},
        ).scalar_one()

    return {
        "database": database_name,
        "table_count": table_count,
    }