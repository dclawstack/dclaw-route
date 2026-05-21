from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.ai import RouteChatRequest, RouteChatResponse
from app.services.route_ai import chat

router = APIRouter()


@router.post("/route-chat", response_model=RouteChatResponse)
async def route_chat(payload: RouteChatRequest, db: AsyncSession = Depends(get_db)):
    return await chat(db, payload.message, payload.history)
