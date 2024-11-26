from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    fam = Column(String, nullable=False)
    name = Column(String, nullable=False)
    otc = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)

    perevals = relationship("PerevalAdded", back_populates="user")
