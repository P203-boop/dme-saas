from fastapi import Form
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import patients, orders, process

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DME SaaS Platform")

# -----------------------
# CORS (for frontend later)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# ROUTES
# -----------------------
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
        return {"error": "Invalid credentials"}

    token = create_access_token({"sub": username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
