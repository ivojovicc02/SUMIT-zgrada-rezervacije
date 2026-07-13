from fastapi import FastAPI
from app.database import Base, engine
from app.routers import spaces
from app.routers import spaces, reservations
from app.routers import spaces, reservations, admin
from app.routers import spaces, reservations, admin, availability

Base.metadata.create_all(bind=engine)  # kreira tablice ako ne postoje

app = FastAPI(title="SUMIT Rezervacije")

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

app.include_router(spaces.router)
app.include_router(reservations.router)
app.include_router(admin.router)
app.include_router(availability.router)