from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Перечисление для статусов
class Status(str, Enum):
    new = "new"
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class UserSchema(BaseModel):
    fam: str
    name: str
    otc: str
    email: EmailStr
    phone: str

    @field_validator("fam", "name", "otc", "email", "phone", mode="before")
    def check_not_empty(cls, value, info):
        if isinstance(value, str) and value.strip() == "":
            raise ValueError(f"Поле '{info.field_name}' не должно быть пустым")
        return value


class CoordsSchema(BaseModel):
    latitude: float
    longitude: float
    height: int


class ImageSchema(BaseModel):
    url: str
    title: str


class LevelSchema(BaseModel):
    winter: str = Field(..., description="Допустимые значения: 1A, 1B, 2A, 2B, 3A, 3B, пустое значение")
    summer: str = Field(..., description="Допустимые значения: 1A, 1B, 2A, 2B, 3A, 3B, пустое значение")
    autumn: str = Field(..., description="Допустимые значения: 1A, 1B, 2A, 2B, 3A, 3B, пустое значение")
    spring: str = Field(..., description="Допустимые значения: 1A, 1B, 2A, 2B, 3A, 3B, пустое значение")

    @field_validator("winter", "summer", "autumn", "spring")
    def check_valid_level(cls, value):
        # Список допустимых значений
        valid_levels = ["1A", "1B", "2A", "2B", "3A", "3B", ""]
        if value not in valid_levels:
            raise ValueError(f"Неверный уровень сложности: {value}")
        return value


class SubmitDataRequest(BaseModel):
    beauty_title: str
    title: str
    other_titles: str
    connect: str
    user: UserSchema
    coords: CoordsSchema
    level: LevelSchema
    images: List[ImageSchema]


class SubmitDataResponse(BaseModel):
    message: str
    share_link: str
    status: str
    beauty_title: Optional[str] = None
    title: Optional[str] = None
    other_titles: Optional[str] = None
    connect: Optional[str] = None
    add_time: datetime
    user: UserSchema
    coords: CoordsSchema
    level: LevelSchema
    images: List[ImageSchema]


class SimpleResponse(BaseModel):
    state: int
    message: str
    share_link: str


class SubmitDataUpdateRequest(BaseModel):
    beauty_title: str
    title: str
    other_titles: str
    connect: str
    coords: CoordsSchema
    level: LevelSchema
    images: List[ImageSchema]
