import os

from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.auth import authenticate_user, create_access_token
from app.database import Base, engine
from app.routers import orders, patients, process

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DME SaaS Platform")

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

app.include_router(patients.router)
app.include_router(orders.router)
app.include_router(process.router)


@app.get("/")
def root():
    return {"message": "DME SaaS API Running"}


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
        "user": username,
    }
