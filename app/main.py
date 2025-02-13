from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.internal import admin
from app.routers import users, auth, addresses, products, categories, orders
from .services.admin import seed_admin_if_none_exist

app = FastAPI()

# Include your routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(addresses.router)
app.include_router(products.router)
app.include_router(admin.router)
app.include_router(categories.router)
app.include_router(orders.router)


# Database initialization on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_admin_if_none_exist()
