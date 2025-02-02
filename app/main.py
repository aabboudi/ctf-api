from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api_v1.general import router as router_general
from .api_v1.player import router as router_player
from .api_v1.admin import router as router_admin
from .api_v1.store import router as router_store

app = FastAPI(
  title="NCC Control Center",
  description="API for NCC Control Center",
  version="0.1.0",
  swagger_ui_parameters={"theme": "dark"}
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "ws://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_general, prefix="/api/v1")
app.include_router(router_player, prefix="/api/v1/player")
app.include_router(router_admin, prefix="/api/v1/admin")
app.include_router(router_store, prefix="/api/v1/store")
