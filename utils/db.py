import os 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv



load_dotenv()

DATABASE_URL = os.getenv("CONNECTION_STRING")

engine = create_engine(str(DATABASE_URL))

LocalSession = sessionmaker(autoflush=False,autocommit=False,bind=engine)


Base = declarative_base()


def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()