from __future__ import annotations
from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

class ProductBase(SQLModel):
    """Shared fields used by both the DB table and API schemas."""
    name: str = Field(...)
    price: float = Field(...)
    original_price: float | None = Field(default=None)
    discount: float | None = Field(default=None)          # percentage, e.g. 12.5
    category: str | None = Field(default=None)
    sub: str | None = Field(default=None)                  # subcategory
    description: str | None = Field(default=None)
    image: str | None = Field(default=None)
    images: list[str] | None = Field(default=None, sa_column=Column(JSON))
    highlights: list[str] | None = Field(default=None, sa_column=Column(JSON))
    features: list[str] | None = Field(default=None, sa_column=Column(JSON))
    rating: float = Field(default=0.0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    in_stock: bool = Field(default=True)
    stock_quantity: int = Field(default=0, ge=0)
    is_featured: bool = Field(default=False)


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    """Schema used when creating a product (no id expected)."""
    pass


class ProductUpdate(SQLModel):
    """Schema used when partially updating a product (all fields optional)."""
    name: str | None = Field(default=None)
    price: float | None = Field(default=None)
    original_price: float | None = Field(default=None)
    discount: float | None = Field(default=None)
    category: str | None = Field(default=None)
    sub: str | None = Field(default=None)
    description: str | None = Field(default=None)
    image: str | None = Field(default=None)
    images: list[str] | None = Field(default=None)
    highlights: list[str] | None = Field(default=None)
    features: list[str] | None = Field(default=None)
    rating: float | None = Field(default=None)
    review_count: int | None = Field(default=None)
    in_stock: bool | None = Field(default=None)
    stock_quantity: int | None = Field(default=None)
    is_featured: bool | None = Field(default=None)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

class CartItemBase(SQLModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItem(CartItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")


class CartItemCreate(CartItemBase):
    """Schema for adding / updating cart items (client never sends user_id or id)."""
    pass


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    price: float


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: str = Field(default="pending")   # pending | confirmed | shipped | delivered | cancelled
    total: float = Field(default=0.0)
    shipping_address: str | None = Field(default=None)   # JSON string or plain text address
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
