from fastapi import FastAPI
from app.database import Base, engine
from app.routers import reservations, admin, availability
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)  # kreira tablice ako ne postoje

app = FastAPI(title="SUMIT Rezervacije")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reservations.router)
app.include_router(admin.router)
app.include_router(availability.router)