from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import payments, simulate, dashboard
import os

app = FastAPI(title="CheckoutGuard AI", version="1.0.0")

# CORS for frontend (if any)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments.router)
app.include_router(simulate.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "CheckoutGuard API is running. Check /docs for endpoints."}

# Mount static files for the dashboard
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="static")
