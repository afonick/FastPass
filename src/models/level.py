from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True)
    winter = Column(String, nullable=True)
    summer = Column(String, nullable=True)
    autumn = Column(String, nullable=True)
    spring = Column(String, nullable=True)

    pereval = relationship("PerevalAdded", back_populates="level")
