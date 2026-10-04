import fastapi
from fastapi import Depends, HTTPException, status
from models import UserOrmModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from depends import *
from schemas import UserUuidResponse

api_users_router = fastapi.routing.APIRouter()


@api_users_router.get(
        "/{user_id}/get_uuid",
        response_model=UserUuidResponse,
        )
async def get_uuid(
        user_id: str, 
        session: AsyncSession = Depends(DatabaseSessionRequired)
    )->dict:
    '''Получить строку uuid для фильтрации материалов'''
    stmt = select(UserOrmModel.id).where(UserOrmModel.user_id == user_id)
    uuid = await session.scalar(stmt)
    

    if uuid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с user_id '{user_id}' не найден"
        )

    return {"uuid": uuid}