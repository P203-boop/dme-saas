from routers import patients, orders, process
from database import Base, engine
from auth import authenticate_user, create_access_token
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os

# -----------------------
# CREATE TABLES
# -----------------------
Base.metadata.create_all(bind=engine)

# -----------------------
# APP INIT
# -----------------------
app = FastAPI(title="DME SaaS Platform")

# -----------------------
# CORS
# -----------------------
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# ROUTERS
# -----------------------
app.include_router(patients.router)
app.include_router(orders.router)
app.include_router(process.router)

# -----------------------
# HEALTH CHECK
# -----------------------


@app.get("/")
def root():
    return {"message": "DME SaaS API Running"}

# -----------------------
# LOGIN ENDPOINT
# -----------------------


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": username})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": username
    }
