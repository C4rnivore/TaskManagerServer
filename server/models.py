from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

import database

class User(database.Base):
    __tablename__ = "users"
    tasks = relationship("Task", back_populates="owner")

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False)
    hashed_password = Column(String)

    


class Task(database.Base):
    __tablename__ = "tasks"
    owner = relationship("User", back_populates="tasks")
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    description = Column(String, index=True)
    

    