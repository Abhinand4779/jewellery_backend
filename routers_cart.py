"""
Shopping-cart routes.  All endpoints require a valid JWT.

GET    /cart/           – view current user's cart (with product details)
POST   /cart/           – add item or increment quantity if already present
PUT    /cart/{item_id}  – set exact quantity for an existing item
DELETE /cart/{item_id}  – remove a single item
DELETE /cart/           – clear entire cart
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

import models
from auth import get_current_active_user
from database import get_session

router = APIRouter(prefix="/cart", tags=["cart"])


# ---------------------------------------------------------------------------
# Helper: enrich cart items with product info for the response
# ---------------------------------------------------------------------------

def _enrich_cart(
    items: List[models.CartItem], session: Session
) -> List[Dict[str, Any]]:
    """Return cart items with a nested `product` snapshot."""
    enriched = []
    for item in items:
        prod = session.get(models.Product, item.product_id)
        enriched.append(
            {
                "id": item.id,
                "user_id": item.user_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": {
                    "id": prod.id,
                    "name": prod.name,
                    "price": prod.price,
                    "image": prod.image,
                    "in_stock": prod.in_stock,
                }
                if prod
                else None,
            }
        )
    return enriched


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/")
def get_cart(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """Return all cart items for the logged-in user, enriched with product details."""
    items = session.exec(
        select(models.CartItem).where(models.CartItem.user_id == current_user.id)
    ).all()
    return _enrich_cart(items, session)


@router.post("/", response_model=models.CartItem, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_in: models.CartItemCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> models.CartItem:
    """
    Add a product to the cart.

    If the product already exists in the cart the quantities are merged
    (upsert behaviour) rather than creating a duplicate row.
    """
    prod = session.get(models.Product, item_in.product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if not prod.in_stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is out of stock")
    if prod.stock_quantity < item_in.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Only {prod.stock_quantity} items in stock")

    # Upsert: merge if the item already exists for this user
    existing = session.exec(
        select(models.CartItem).where(
            models.CartItem.user_id == current_user.id,
            models.CartItem.product_id == item_in.product_id,
        )
    ).first()

    if existing:
        new_qty = existing.quantity + item_in.quantity
        if prod.stock_quantity < new_qty:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Cannot add {item_in.quantity}. Cart has {existing.quantity}, total would exceed stock ({prod.stock_quantity})."
            )
        existing.quantity = new_qty
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    new_item = models.CartItem(
        user_id=current_user.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity,
    )
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item


@router.put("/{item_id}", response_model=models.CartItem)
def update_cart_item(
    item_id: int,
    item_in: models.CartItemCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> models.CartItem:
    """Set the exact quantity for a cart item.  Use quantity=0 to remove it."""
    existing = session.get(models.CartItem, item_id)
    if not existing or existing.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    if item_in.quantity <= 0:
        session.delete(existing)
        session.commit()
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)   # item removed

    prod = session.get(models.Product, existing.product_id)
    if not prod:
         # Should ideally delete the cart item if product is gone, but let's just error
        raise HTTPException(status_code=404, detail="Product associated with cart item not found")

    if prod.stock_quantity < item_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot update quantity to {item_in.quantity}. Only {prod.stock_quantity} in stock."
        )

    existing.quantity = item_in.quantity
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> None:
    """Remove a single item from the cart."""
    existing = session.get(models.CartItem, item_id)
    if not existing or existing.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    session.delete(existing)
    session.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> None:
    """Remove every item from the current user's cart."""
    items = session.exec(
        select(models.CartItem).where(models.CartItem.user_id == current_user.id)
    ).all()
    for item in items:
        session.delete(item)
    session.commit()
