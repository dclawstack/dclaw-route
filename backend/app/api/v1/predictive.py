from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.predictive import RouteForecastRead, WeatherState, WeatherUpdate
from app.services.predictive import (
    forecast_route,
    get_weather_factor,
    set_weather_factor,
)

router = APIRouter()


@router.get("/weather", response_model=WeatherState)
async def get_weather():
    return WeatherState(factor=get_weather_factor())


@router.post("/weather", response_model=WeatherState)
async def post_weather(payload: WeatherUpdate):
    try:
        set_weather_factor(payload.factor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return WeatherState(factor=get_weather_factor())


@router.get("/routes/{route_id}/forecast", response_model=RouteForecastRead)
async def route_forecast(route_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        f = await forecast_route(db, route_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return RouteForecastRead(**f.__dict__)
