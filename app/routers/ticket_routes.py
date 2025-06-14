from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ticket, Responder, TicketUpdate, User
from app import models, schemas, auth
from app.schemas import TicketUpdateCreate, TicketUpdateOut
from app.auth import get_db, get_current_user
#from app.schemas import TicketOut

ticket_router = APIRouter()

@ticket_router.put("/tickets/{ticket_id}/assign/{responder_id}")
def assign_responder(ticket_id: int, responder_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    responder = db.query(Responder).filter(Responder.id == responder_id).first()
    if not responder:
        raise HTTPException(status_code=404, detail="Responder not found")

    ticket.assigned_to = responder.user_id
    db.commit()
    db.refresh(ticket)

    return {"message": f"Ticket {ticket_id} assigned to responder {responder_id}"}

@ticket_router.get("/responder-dashboard", response_model=list[schemas.Ticket])
def responder_dashboard(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role != "responder":
        raise HTTPException(status_code=403, detail="Access forbidden")

    tickets = db.query(models.Ticket).filter(
        (models.Ticket.status != "closed") | (models.Ticket.assigned_to == None)
    ).all()
    return tickets

@ticket_router.put("/tickets/{ticket_id}/assign", response_model=schemas.Ticket)
def assign_ticket_to_self(
    ticket_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role != "responder":
        raise HTTPException(status_code=403, detail="Only responders can assign tickets.")

    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.assigned_to = current_user.id
    ticket.status = "in_progress"
    db.commit()
    db.refresh(ticket)
    return ticket
