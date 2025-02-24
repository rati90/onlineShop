from .users import router as users_router
from .auth import router as auth_router
from .addresses import router as addresses_router
from .products import router as products_router
from .categories import router as categories_router
from .orders import router as orders_router
from .payments import router as payments_router
from app.internal import admin

# List of routers
routers = [
    auth_router,
    users_router,
    addresses_router,
    products_router,
    admin.router,
    categories_router,
    orders_router,
    payments_router,
]
