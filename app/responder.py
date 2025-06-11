# app/models/responder.py

from sqlalchemy import Column, Integer, String
from app.database import Base

class Responder(Base):
    __tablename__ = "responders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    specialization = Column(String, nullable=True)  # e.g. "network", "hardware", etc.

