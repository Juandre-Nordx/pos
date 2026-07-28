from fastapi import APIRouter

from app.api.v1.auth.routes import router as auth_router
from app.api.v1.clients.routes import router as clients_router
from app.api.v1.dashboard.routes import router as dashboard_router
from app.api.v1.inventory.routes import router as inventory_router
from app.api.v1.ppe.routes import router as ppe_router
from app.api.v1.settings.routes import router as settings_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(clients_router)
api_router.include_router(inventory_router)
api_router.include_router(ppe_router)
api_router.include_router(settings_router)
