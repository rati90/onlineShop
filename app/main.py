from fastapi import Depends, FastAPI
from .internal import admin
from .routers import items, users, auth
from .db.database import create_db_and_tables
from .dependencies.auth import get_current_user  # Use get_current_user for protected routes

app = FastAPI()

# Include authentication-related routes
app.include_router(auth.router)

# Include user-related routes
app.include_router(users.router)

# Include item-related routes
app.include_router(items.router)

# Include admin routes with authentication
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_user)],  # Protect admin routes
    responses={418: {"description": "I'm a teapot"}},
)

# Database initialization on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
