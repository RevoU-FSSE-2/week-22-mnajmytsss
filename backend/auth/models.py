from sqlalchemy import Column, Integer, String
from db import db

class User(db.Model):
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    role = Column(String(10), nullable=False)