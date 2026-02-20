"""
Product routes.

Public endpoints (no auth required)
-------------------------------------
GET  /products/                       – list all products (with optional filters)
GET  /products/{product_id}           – single product detail
GET  /products/category/{category}    – filter by category
GET  /products/search                 – full-text search on name / description

Admin-only endpoints
---------------------
POST   /products/            – create product
PUT    /products/{product_id} – replace product
PATCH  /products/{product_id} – partial update
DELETE /products/{product_id} – delete product
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

import models
from auth import require_admin
from database import get_session

router = APIRouter(prefix="/products", tags=["products"])


# ---------------------------------------------------------------------------
# Public – read
# ---------------------------------------------------------------------------

@router.get("/search", response_model=List[models.Product])
def search_products(
    q: str = Query(..., min_length=1, description="Search term"),
    session: Session = Depends(get_session),
) -> List[models.Product]:
    """Case-insensitive keyword search across product name and description."""
    term = f"%{q.lower()}%"
    results = session.exec(
        select(models.Product).where(
            models.Product.name.ilike(term)  # type: ignore[attr-defined]
            | models.Product.description.ilike(term)  # type: ignore[attr-defined]
        )
    ).all()
    return results


@router.get("/category/{category}", response_model=List[models.Product])
def products_by_category(
    category: str,
    sub: Optional[str] = Query(None, description="Filter by sub-category"),
    in_stock: Optional[bool] = Query(None),
    featured: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> List[models.Product]:
    """Return products filtered by category with optional sub-category and stock filters."""
    stmt = select(models.Product).where(
        models.Product.category == category
    )
    if sub is not None:
        stmt = stmt.where(models.Product.sub == sub)
    if in_stock is not None:
        stmt = stmt.where(models.Product.in_stock == in_stock)
    if featured is not None:
        stmt = stmt.where(models.Product.is_featured == featured)
    stmt = stmt.offset(skip).limit(limit)
    return session.exec(stmt).all()


@router.get("/", response_model=List[models.Product])
def list_products(
    category: Optional[str] = Query(None),
    sub: Optional[str] = Query(None),
    in_stock: Optional[bool] = Query(None),
    featured: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> List[models.Product]:
    """List all products with optional filtering and pagination."""
    stmt = select(models.Product)
    if category is not None:
        stmt = stmt.where(models.Product.category == category)
    if sub is not None:
        stmt = stmt.where(models.Product.sub == sub)
    if in_stock is not None:
        stmt = stmt.where(models.Product.in_stock == in_stock)
    if featured is not None:
        stmt = stmt.where(models.Product.is_featured == featured)
    stmt = stmt.offset(skip).limit(limit)
    return session.exec(stmt).all()


@router.get("/{product_id}", response_model=models.Product)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
) -> models.Product:
    prod = session.get(models.Product, product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return prod


# ---------------------------------------------------------------------------
# Admin – write
# ---------------------------------------------------------------------------

@router.post("/", response_model=models.Product, status_code=status.HTTP_201_CREATED)
def create_product(
    prod_in: models.ProductCreate,
    session: Session = Depends(get_session),
    _admin: models.User = Depends(require_admin),
) -> models.Product:
    """Create a new product. Admin only."""
    db_prod = models.Product.from_orm(prod_in)
    session.add(db_prod)
    session.commit()
    session.refresh(db_prod)
    return db_prod


@router.put("/{product_id}", response_model=models.Product)
def replace_product(
    product_id: int,
    prod_in: models.ProductCreate,
    session: Session = Depends(get_session),
    _admin: models.User = Depends(require_admin),
) -> models.Product:
    """Fully replace a product. Admin only."""
    existing = session.get(models.Product, product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    # Apply every field from the incoming data
    for key, val in prod_in.dict().items():
        setattr(existing, key, val)
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


@router.patch("/{product_id}", response_model=models.Product)
def update_product(
    product_id: int,
    prod_in: models.ProductUpdate,
    session: Session = Depends(get_session),
    _admin: models.User = Depends(require_admin),
) -> models.Product:
    """Partially update a product (only send the fields you want to change). Admin only."""
    existing = session.get(models.Product, product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    for key, val in prod_in.dict(exclude_unset=True).items():
        setattr(existing, key, val)
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
    _admin: models.User = Depends(require_admin),
) -> None:
    """Delete a product. Admin only."""
    prod = session.get(models.Product, product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    session.delete(prod)
    session.commit()
