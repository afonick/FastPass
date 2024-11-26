from fastapi import Depends
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine, AsyncConnection)
from src.core.config import settings
from typing import Union, Callable, Annotated


class InternalError(Exception):
    pass


# Функция для получения асинхронной сессии
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except InternalError:
            await session.rollback()


# Функция для создания фабрики сессий
def create_sessionmaker(
    bind_engine: Union[AsyncEngine, AsyncConnection]
) -> Callable[..., async_sessionmaker]:
    return async_sessionmaker(
        bind=bind_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


# Создание асинхронного движка для подключения к PostgreSQL
engine = create_async_engine(settings.postgres_dsn)
engine_null_pool = create_async_engine(settings.postgres_dsn, poolclass=NullPool)

# Создание фабрики сессий
async_session = create_sessionmaker(engine)
async_session_null_pool = async_sessionmaker(bind=engine_null_pool)

# Создание зависимости для работы с базой данных
db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
