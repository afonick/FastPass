from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class PerevalImages(Base):
    __tablename__ = "pereval_images"

    id = Column(Integer, primary_key=True)
    pereval_id = Column(Integer, ForeignKey("pereval_added.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String, nullable=False)
    title = Column(String, nullable=False)

    pereval = relationship("PerevalAdded", back_populates="images")
