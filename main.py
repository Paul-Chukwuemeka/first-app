from fastapi import FastAPI
from utils.db import Base,engine
from routes import auth,products,cart
from fastapi.middleware.cors import CORSMiddleware
# from models import userModel,product_model,cart_model

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # can be ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],     # GET, POST, PUT, DELETE...
    allow_headers=["*"],     # Accept all headers
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)


