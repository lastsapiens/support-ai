from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app import schemas, models, auth
from app.database import Base, engine
from app.auth import (
    get_db, get_current_user, create_access_token,
    get_password_hash, authenticate_user
)
from app.routers import tickets  # <-- Add this line if not already
from app.routers.ticket_routes import ticket_router

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at "/"
@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("static/index.html")


# ✅ Signup route (based on username, not email)
@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check for existing username
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        role=user.role or "user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ✅ Login route (username-based login)
@app.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ✅ Dashboard route
@app.get("/dashboard", response_model=schemas.UserOut)
def dashboard(current_user: schemas.UserOut = Depends(get_current_user)):
    return current_user


# ✅ Register the ticket router
app.include_router(tickets.router)        # <-- For regular ticket creation
app.include_router(ticket_router, tags=["Tickets"])
