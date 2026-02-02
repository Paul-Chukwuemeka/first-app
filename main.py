from fastapi import FastAPI
from utils.db import Base,engine
from routes import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth.router)
