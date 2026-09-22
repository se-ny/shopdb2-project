from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_category_id = Column(BigInteger, ForeignKey("categories.category_id"), nullable=True)
    category_name = Column(String(100), nullable=False)
    category_level = Column(Integer, default=1)
    display_order = Column(Integer, default=0)
    active_yn = Column(String(1), default="Y")

    children = relationship("Category", viewonly=True)