from fastapi import FastAPI
from database import engine
from routers import user_router, product, seller_product, browse, cart
from models.base import Base
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router, prefix="/api/users", tags=["users"])
app.include_router(product.router, prefix="/api/products", tags=["products"])
app.include_router(seller_product.router, prefix="/api/seller-products", tags=["seller-products"])
app.include_router(browse.router, prefix="/api/browse", tags=["browse"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])