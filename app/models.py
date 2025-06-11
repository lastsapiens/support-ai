from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from .responder import Responder  # <-- Add this line!

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open")  # open, in_progress, closed
    #priority = Column(String(20), nullable=False, default="medium")  # low, medium, high
    priority = Column(String, nullable=True) #temp
    category = Column(String(50), nullable=True)
    wing = Column(String, nullable=True)
    section = Column(String, nullable=True)
    attachment_url = Column(String, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")

    responder_id = Column(Integer, ForeignKey("responders.id"), nullable=True)
    responder = relationship("Responder")

    assigned_user = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="assigned_tickets",
        post_update=True
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    # Specify foreign_keys explicitly here:
    tickets = relationship("Ticket", foreign_keys=[Ticket.user_id], back_populates="user")
    assigned_tickets = relationship("Ticket", foreign_keys=[Ticket.assigned_to], back_populates="assigned_user")

