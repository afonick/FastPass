from fastapi import APIRouter
from .submit import submit_router

api_router = APIRouter()

api_router.include_router(submit_router)
