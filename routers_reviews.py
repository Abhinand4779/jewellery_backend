"""
Reviews routes.

GET    /reviews/product/{product_id}  – list reviews for a product
POST   /reviews/product/{product_id}  – add a review (auth required)
DELETE /reviews/{id}                  – delete a review (owner or admin)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

import models
from auth import get_current_active_user
from database import get_session

router = APIRouter(prefix="/reviews", tags=["reviews"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = Field(default=None)


class ReviewOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str] = Field(default=None)
    created_at: str
    user_name: Optional[str] = Field(default=None)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/product/{product_id}", response_model=List[ReviewOut])
def get_product_reviews(
    product_id: int,
    session: Session = Depends(get_session),
) -> List[ReviewOut]:
    """Get all reviews for a specific product."""
    reviews = session.exec(
        select(models.Review).where(models.Review.product_id == product_id)
    ).all()
    
    # Enrich with user name
    results = []
    for r in reviews:
        user = session.get(models.User, r.user_id)
        results.append({
            "id": r.id,
            "user_id": r.user_id,
            "product_id": r.product_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
            "user_name": user.full_name if user else "Anonymous"
        })
    return results


@router.post("/product/{product_id}", response_model=models.Review, status_code=status.HTTP_201_CREATED)
def create_review(
    product_id: int,
    review_in: ReviewCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> models.Review:
    """Add a review for a product."""
    # Check if product exists
    product = session.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if user already reviewed? Typically allowed multiple, or restrict one per user?
    # Let's allow multiple for now as per simple requirements.

    review = models.Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    
    # Update product rating and review count
    # This is a bit heavy for every review, but keeps data consistent.
    # Recalculate average
    all_reviews = session.exec(
        select(models.Review).where(models.Review.product_id == product_id)
    ).all()
    
    total_rating = sum(r.rating for r in all_reviews)
    count = len(all_reviews)
    
    product.rating = total_rating / count if count > 0 else 0
    product.review_count = count
    session.add(product)
    session.commit()
    
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> None:
    """Delete a review. Only the author or an admin can delete it."""
    review = session.get(models.Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    if review.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
        
    product_id = review.product_id
    session.delete(review)
    session.commit()
    
    # Update product stats again
    product = session.get(models.Product, product_id)
    if product:
        remaining_reviews = session.exec(
            select(models.Review).where(models.Review.product_id == product_id)
        ).all()
        total_rating = sum(r.rating for r in remaining_reviews)
        count = len(remaining_reviews)
        product.rating = total_rating / count if count > 0 else 0
        product.review_count = count
        session.add(product)
        session.commit()
