from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

class ProductBase(SQLModel):
    """Shared fields used by both the DB table and API schemas."""
    name: str
    price: float
    original_price: Optional[float] = None
    discount: Optional[float] = None          # percentage, e.g. 12.5
    category: Optional[str] = None
    sub: Optional[str] = None                  # subcategory
    description: Optional[str] = None
    image: Optional[str] = None
    images: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    highlights: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    features: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    rating: float = Field(default=0.0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    in_stock: bool = True
    stock_quantity: int = Field(default=0, ge=0)
    is_featured: bool = False


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    """Schema used when creating a product (no id expected)."""
    pass


class ProductUpdate(SQLModel):
    """Schema used when partially updating a product (all fields optional)."""
    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount: Optional[float] = None
    category: Optional[str] = None
    sub: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None
    highlights: Optional[List[str]] = None
    features: Optional[List[str]] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    is_featured: Optional[bool] = None


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
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
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")


class CartItemCreate(CartItemBase):
    """Schema for adding / updating cart items (client never sends user_id or id)."""
    pass


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    price: float


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: str = Field(default="pending")   # pending | confirmed | shipped | delivered | cancelled
    total: float = 0.0
    shipping_address: Optional[str] = None   # JSON string or plain text address
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
