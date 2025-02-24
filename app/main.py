from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.routers import routers
from .services.admin import seed_admin_if_none_exist

app = FastAPI()

# Include your routers
for router in routers:
    app.include_router(router)


# Database initialization on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_admin_if_none_exist()
