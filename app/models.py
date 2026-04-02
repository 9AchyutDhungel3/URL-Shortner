from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_clicked = Column(DateTime, nullable=True)