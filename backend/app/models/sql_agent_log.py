from sqlalchemy import Column, BigInteger, String, Text, Enum, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class SqlAgentQueryLog(Base):
    __tablename__ = "sql_agent_query_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    log_code = Column(String(50), unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    question_text = Column(Text, nullable=True)
    generated_sql = Column(Text, nullable=True)
    execution_status = Column(Enum("SUCCESS", "BLOCKED", "ERROR", name="sql_agent_status_enum"), nullable=False)
    result_summary = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())