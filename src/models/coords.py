from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship
from .base import Base


class Coords(Base):
    __tablename__ = "coords"

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)

    perevals = relationship("PerevalAdded", back_populates="coords")
