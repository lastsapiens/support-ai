from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ticket, TicketUpdate, User
from app.schemas import TicketUpdateCreate, TicketUpdateOut
from app.auth import get_current_user

responder_router = APIRouter()


@responder_router.post("/tickets/{ticket_id}/update", response_model=TicketUpdateOut)
def update_ticket(
    ticket_id: int,
    update: TicketUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if ticket exists
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Only responder can update
    if current_user.role != "responder":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update status
    if update.status:
        ticket.status = update.status

    # Create comment update
    update_obj = TicketUpdate(
        ticket_id=ticket_id,
        responder_id=current_user.id,
        comment=update.comment
    )

    db.add(update_obj)
    db.commit()
    db.refresh(update_obj)

    return TicketUpdateOut(
        id=update_obj.id,
        comment=update_obj.comment,
        created_at=update_obj.created_at,
        responder_id=current_user.id,
        responder_name=current_user.username
    )


@responder_router.get("/tickets/{ticket_id}/history", response_model=list[TicketUpdateOut])
def get_ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only responder can view
    if current_user.role != "responder":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Get all updates
    updates = db.query(TicketUpdate).filter(
        TicketUpdate.ticket_id == ticket_id
    ).order_by(TicketUpdate.created_at.asc()).all()

    return [
        TicketUpdateOut(
            id=upd.id,
            comment=upd.comment,
            created_at=upd.created_at,
            responder_id=upd.responder_id,
            responder_name=upd.responder.username if upd.responder else "Unknown"
        )
        for upd in updates
    ]
