from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.auth import get_db, get_current_user
from fastapi import UploadFile, File, Form
import os
import shutil
from app import models

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)

@router.post("/", response_model=schemas.Ticket)
async def create_ticket(
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
    category: str = Form(None),
    wing: str = Form(None),
    section: str = Form(None),
    attachment: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    attachment_url = None
    if attachment:
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, attachment.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(attachment.file, f)
        attachment_url = f"/{file_path}"

    ticket = models.Ticket(
        title=title,
        description=description,
        priority=priority,
        category=category,
        wing=wing,
        section=section,
        attachment_url=attachment_url,
        user_id=current_user.id
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/", response_model=list[schemas.Ticket])
def read_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud.get_tickets_for_user(db, current_user.id)  # 🔁 use ID instead of email

#@router.get("/{ticket_id}", response_model=schemas.Ticket)
#def read_ticket(
    #ticket_id: int,
    #db: Session = Depends(get_db),
    #current_user=Depends(get_current_user),
#):
    #ticket = crud.get_ticket(db, ticket_id)
    #if not ticket or ticket.user_id != current_user.id:  # 🔁 compare by ID
        #raise HTTPException(status_code=404, detail="Ticket not found")
    #return ticket

@router.get("/tickets/")
def read_tickets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return crud.get_tickets_for_user(db, current_user.id)


@router.patch("/{ticket_id}", response_model=schemas.Ticket)
def update_ticket(
    ticket_id: int,
    status: schemas.TicketUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket or ticket.user_id != current_user.id:  # 🔁 compare by ID
        raise HTTPException(status_code=404, detail="Ticket not found")
    return crud.update_ticket_status(db, ticket_id, status.status)
