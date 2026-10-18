from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.companies import router as company_router
from app.api.routes.users import router as users_router
from app.api.routes.auth import router as auth_router
from app.api.routes.uploads import router as uploads_router
from app.api.routes.forecasts import router as forecasts_router
from app.api.routes.recommendations import router as recommendations_router


app = FastAPI(
    title="MUGONEXT",
    version="1.0.0",
    description="MUGONEXT AI Business Intelligence & Forecasting Platform",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://mugonext.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(health_router)
app.include_router(company_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(uploads_router)
app.include_router(forecasts_router)
app.include_router(recommendations_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "MUGONEXT API is running",
        "version": "1.0.0",
    }