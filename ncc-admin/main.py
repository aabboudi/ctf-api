from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.api_v1 import router as api_v1_router

app = FastAPI(
  title="NCC Control Center",
  description="API for NCC Control Center",
  version="0.1.0",
  swagger_ui_parameters={"theme": "dark"}
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")
