from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

from auth import authenticate_user, create_access_token
from database import Base, engine
from routers import patients, orders, process

# -----------------------
# CREATE TABLES
# -----------------------
Base.metadata.create_all(bind=engine)

# -----------------------
# APP INIT
# -----------------------
app = FastAPI(title="DME SaaS Platform")

# -----------------------
# CORS (for frontend / Streamlit)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


@app.get("/")
def root():
    return {"message": "DME SaaS API Running"}


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        user = authenticate_user(username, password)

        if not user:
            return {"error": "Invalid credentials"}

        token = create_access_token({"sub": username})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except Exception as e:
        return {"error": str(e)}
