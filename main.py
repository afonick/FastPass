import atexit
import logging
import logging.config
import logging.handlers
from queue import Queue
from contextlib import asynccontextmanager
from typing import AsyncContextManager

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse

from src.core.config import uvicorn_options
from src.api.v1 import api_router
from src.core.logger import setup_logging, LOGGING_CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    logging.config.dictConfig(LOGGING_CONFIG)
    log_queue = Queue(-1)

    # Получаем корневой логгер и находим обработчик очереди
    root_logger = logging.getLogger()
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, *root_logger.handlers)

    # Добавляем QueueHandler к корневому логгеру
    root_logger.addHandler(queue_handler)

    try:
        listener.start()
        atexit.register(listener.stop)
        yield
    finally:
        listener.stop()


setup_logging()
app = FastAPI(lifespan=lifespan, docs_url="/api/openapi")
logger = logging.getLogger("my_app")

# Добавление роутеров
app.include_router(api_router)


# Middleware для обработки ошибок
@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        logger.error(f"{request.url} | HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail}
        )
    except Exception as e:
        logger.error(f"{request.url} | Error in application: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )


# Обработчики исключений
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"{request.url} | Error in application: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"{request.url} | HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


if __name__ == '__main__':
    print(uvicorn_options)
    uvicorn.run('main:app', **uvicorn_options)
