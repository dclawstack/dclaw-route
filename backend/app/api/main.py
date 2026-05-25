from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import health
from app.api.v1 import stops, drivers, routes, deliveries, ai, tracking, driver_shifts, vehicles, notifications, returns, territories, analytics, wms, predictive, gig, av, carbon, demo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(stops.router, prefix="/api/v1/stops", tags=["stops"])
app.include_router(drivers.router, prefix="/api/v1/drivers", tags=["drivers"])
app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
app.include_router(deliveries.router, prefix="/api/v1/deliveries", tags=["deliveries"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(tracking.router, prefix="/api/v1/tracking", tags=["tracking"])
app.include_router(driver_shifts.router, prefix="/api/v1/shifts", tags=["shifts"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(returns.router, prefix="/api/v1/returns", tags=["returns"])
app.include_router(territories.router, prefix="/api/v1/territories", tags=["territories"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(wms.router, prefix="/api/v1/wms", tags=["wms"])
app.include_router(predictive.router, prefix="/api/v1/predictive", tags=["predictive"])
app.include_router(gig.router, prefix="/api/v1/gig", tags=["gig"])
app.include_router(av.router, prefix="/api/v1/av", tags=["av"])
app.include_router(carbon.router, prefix="/api/v1/carbon", tags=["carbon"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])
