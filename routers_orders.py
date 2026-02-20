"""
Order routes.

User endpoints
--------------
POST /orders/               – checkout: convert cart → order
GET  /orders/               – list current user's orders
GET  /orders/{order_id}     – detail for a single order (with order-items)

Admin endpoints
---------------
GET  /orders/admin/all                          – list every order
PATCH /orders/admin/{order_id}/status           – update order status
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

import models
from auth import get_current_active_user, require_admin
from database import get_session

router = APIRouter(prefix="/orders", tags=["orders"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _order_detail(order: models.Order, session: Session) -> Dict[str, Any]:
    """Attach order-items (with product snapshots) to an order dict."""
    items = session.exec(
        select(models.OrderItem).where(models.OrderItem.order_id == order.id)
    ).all()

    items_out = []
    for oi in items:
        prod = session.get(models.Product, oi.product_id)
        items_out.append(
            {
                "id": oi.id,
                "product_id": oi.product_id,
                "quantity": oi.quantity,
                "price": oi.price,
                "product_name": prod.name if prod else None,
                "product_image": prod.image if prod else None,
            }
        )

    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at,
        "items": items_out,
    }


class StatusUpdate(BaseModel):
    status: str  # pending | confirmed | shipped | delivered | cancelled


VALID_STATUSES = {"pending", "confirmed", "shipped", "delivered", "cancelled"}


# ---------------------------------------------------------------------------
# User routes
# ---------------------------------------------------------------------------

class OrderCreate(BaseModel):
    shipping_address: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Convert the authenticated user's cart into a new order.

    * All cart items are moved into OrderItems.
    * Cart is cleared after a successful checkout.
    * Products that no longer exist in the DB are skipped.
    """
    cart_items = session.exec(
        select(models.CartItem).where(models.CartItem.user_id == current_user.id)
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty"
        )

    order = models.Order(
        user_id=current_user.id,
        shipping_address=order_in.shipping_address
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    total = 0.0
    for ci in cart_items:
        prod = session.get(models.Product, ci.product_id)
        if not prod:
            session.delete(ci) # Cleanup invalid cart item
            continue  # product deleted since it was added to cart – skip it
            
        # Check stock
        if prod.stock_quantity < ci.quantity:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Insufficient stock for product '{prod.name}'. Available: {prod.stock_quantity}, Requested: {ci.quantity}"
            )

        # Deduct stock
        prod.stock_quantity -= ci.quantity
        if prod.stock_quantity == 0:
            prod.in_stock = False
        session.add(prod)

        oi = models.OrderItem(
            order_id=order.id,
            product_id=prod.id,
            quantity=ci.quantity,
            price=prod.price,
        )
        total += prod.price * ci.quantity
        session.add(oi)
        session.delete(ci)   # clear cart item

    order.total = total
    session.add(order)
    session.commit()
    session.refresh(order)

    return _order_detail(order, session)


@router.get("/")
def list_user_orders(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    """Return all orders placed by the current user (newest first)."""
    orders = session.exec(
        select(models.Order)
        .where(models.Order.user_id == current_user.id)
        .order_by(models.Order.created_at.desc())  # type: ignore[attr-defined]
    ).all()
    return [_order_detail(o, session) for o in orders]


@router.get("/{order_id}")
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Return a single order that belongs to the current user."""
    order = session.get(models.Order, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return _order_detail(order, session)


# ---------------------------------------------------------------------------
# Admin routes   (prefix /orders/admin/... to avoid path conflicts)
# ---------------------------------------------------------------------------

@router.get("/admin/all")
def list_all_orders(
    session: Session = Depends(get_session),
    _admin: models.User = Depends(require_admin),
) -> List[Dict[str, Any]]:
    """Return every order in the system. Admin only."""
    orders = session.exec(
        select(models.Order).order_by(models.Order.created_at.desc())  # type: ignore[attr-defined]
    ).all()
    return [_order_detail(o, session) for o in orders]


@router.patch("/admin/{order_id}/status")
def update_order_status(
    order_id: int,
    body: StatusUpdate,
    session: Session = Depends(get_session),
    _admin: models.User = Depends(require_admin),
) -> Dict[str, Any]:
    """Update the fulfillment status of an order. Admin only."""
    if body.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
        )
    order = session.get(models.Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    order.status = body.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return _order_detail(order, session)
