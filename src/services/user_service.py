import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User
from src.schemas.submit import UserSchema
from fastapi import HTTPException

logger = logging.getLogger("my_app")


class InvalidUserDataError(Exception):
    pass


# Функция для создания или получения пользователя
async def get_or_create_user(db: AsyncSession, user_data: UserSchema) -> User:
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        # Если пользователя с таким email нет, создаем нового
        user = User(
            fam=user_data.fam,
            name=user_data.name,
            otc=user_data.otc,
            email=user_data.email,
            phone=user_data.phone
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(
            f"Создан новый пользователь с email: {user.email.encode('utf-8', 'ignore').decode('utf-8')}"
        )
    else:
        # Если пользователь найден и ФИО отличаются
        if (user.fam != user_data.fam or
            user.name != user_data.name or
                user.otc != user_data.otc):
            logger.info(f"Пользователь с email {user.email} найден, но ФИО не совпадают.")
            logger.info(f"ФИО в базе: {user.fam} {user.name} {user.otc}")
            logger.info(f"Переданные ФИО: {user_data.fam} {user_data.name} {user_data.otc}")
            # Возвращаем ошибку в API с сообщением о несоответствии ФИО
            raise HTTPException(
                status_code=400,
                detail=f"Под данным email {user.email} уже есть другие ФИО: {user.fam} {user.name} {user.otc}"
            )
        else:
            logger.info(f"Пользователь с email {user.email} найден и данные совпадают")

    return user
