from fastapi import FastAPI
from utils.db import Base,engine
from routes import auth,products
from models import userModel,product_model

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth.router)
app.include_router(products.router)
