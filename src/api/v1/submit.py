import logging
from typing import Union, List

from fastapi import APIRouter, HTTPException

from src.models.pereval import Status
from src.db.db import db_dependency
from src.schemas.submit import SubmitDataRequest, SubmitDataResponse, SimpleResponse, SubmitDataUpdateRequest
from src.services.db_service import SubmitService
from src.services.user_service import get_or_create_user

submit_router = APIRouter(prefix="/submit", tags=["submit"])
logger = logging.getLogger("my_app")


@submit_router.post("/submitData", response_model=Union[SubmitDataResponse, SimpleResponse], name="Создать перевал")
async def create_pereval(data: SubmitDataRequest, db: db_dependency):
    logger.info(f"Создание перевала для пользователя с email: {data.user.email}")

    if not data:
        logger.error("Получены пустые данные")
        raise HTTPException(status_code=400, detail="Ошибка: Данные не были переданы")
    if not data.user:
        logger.error("Данные пользователя отсутствуют")
        raise HTTPException(status_code=400, detail="Ошибка: Данные пользователя не были переданы")

    user = await get_or_create_user(db, data.user)
    service = SubmitService(db)
    return await service.create_pereval(data, user)


@submit_router.get("/submitData/", response_model=List[SubmitDataResponse], name="Получить все перевалы")
async def get_all_perevals(db: db_dependency):
    """Получение всех перевалов."""
    logger.info("Получение всех перевалов")

    service = SubmitService(db)
    return await service.get_all_perevals()


@submit_router.get("/submitData/by_user/", response_model=List[SubmitDataResponse], name="Получить перевалы по email пользователя")
async def get_perevals_by_user_email(user__email: str, db: db_dependency):
    logger.info(f"Получение всех перевалов для пользователя с email: {user__email}")
    service = SubmitService(db)
    return await service.get_perevals_by_user_email(user__email)


@submit_router.get("/submitData/{pereval_id}", response_model=SubmitDataResponse, name="Получить перевал по ID")
async def get_pereval(pereval_id: int, db: db_dependency):
    logger.info(f"Получение перевала с ID: {pereval_id}")

    service = SubmitService(db)
    return await service.get_pereval(pereval_id)


@submit_router.patch("/submitData/{pereval_id}", response_model=SimpleResponse, name="Обновить запись перевала")
async def patch_submit_data(pereval_id: int, data: SubmitDataUpdateRequest, db: db_dependency):
    logger.info(f"Обновление записи перевала с ID: {pereval_id}")

    service = SubmitService(db)
    response = await service.update_pereval(pereval_id, data)
    return response


@submit_router.patch("/submitData/update-status/{pereval_id}", name="Обновить статус перевала")
async def update_pereval_status(pereval_id: int, status: Status, db: db_dependency):
    logger.info(f"Обновление статуса перевала с ID: {pereval_id} на {status}")

    service = SubmitService(db)
    return await service.update_pereval_status(pereval_id, status)
