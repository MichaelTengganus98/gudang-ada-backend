from fastapi import FastAPI
from database import Base, engine
from routers import user_router
from models import user

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router.router, prefix="/api/users", tags=["users"])