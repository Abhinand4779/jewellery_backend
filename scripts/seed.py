"""
scripts/seed.py
---------------
Populates the SQLite database with demo products and an admin user.

Usage (from the jewellery_backend root):
    python scripts/seed.py

Options:
    --reset   Drop and recreate every row before seeding  (default: skip if data exists)
"""

import sys
import os
import argparse

# Make sure the project root is on the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from sqlmodel import Session, select
from database import engine, init_db
from auth import get_password_hash
import models


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

PRODUCTS = [
    # ── Rings ──────────────────────────────────────────────────────────────
    models.ProductCreate(
        name="Solitaire Diamond Ring",
        price=28000, original_price=32000, discount=12.5,
        category="rings", sub="solitaire",
        description="Stunning solitaire diamond ring with certified diamond stone",
        image="/images/rings.jpg",
        images=["/images/rings.jpg", "/images/rings-2.jpg"],
        rating=4.8, review_count=245,
        in_stock=True, stock_quantity=15, is_featured=True,
        highlights=["100% Certified", "Hallmarked Gold", "Lifetime Warranty"],
        features=["Free Shipping", "Easy Returns", "30-Day Exchange"],
    ),
    models.ProductCreate(
        name="Halo Diamond Ring",
        price=32000, original_price=38000, discount=15.8,
        category="rings", sub="halo",
        description="Elegant halo diamond ring with surrounding diamonds",
        image="/images/rings.jpg",
        images=["/images/rings.jpg", "/images/rings-2.jpg"],
        rating=4.7, review_count=189,
        in_stock=True, stock_quantity=10, is_featured=True,
        highlights=["100% Certified", "22K Gold", "BIS Hallmarked"],
    ),
    models.ProductCreate(
        name="Stackable Gold Ring Set",
        price=9500, original_price=11000, discount=13.6,
        category="rings", sub="stackable",
        description="Beautiful set of 3 stackable gold rings for everyday wear",
        image="/images/rings.jpg",
        images=["/images/rings.jpg"],
        rating=4.5, review_count=412,
        in_stock=True, stock_quantity=50,
        highlights=["Light Weight", "Daily Wear", "Elegant Design"],
    ),
    models.ProductCreate(
        name="Twisted Band Ring",
        price=6500, original_price=7800, discount=16.7,
        category="rings", sub="band",
        description="Minimalist twisted gold band ring for everyday elegance",
        image="/images/rings.jpg",
        images=["/images/rings.jpg"],
        rating=4.3, review_count=98,
        in_stock=True, stock_quantity=30,
        highlights=["18K Gold", "Minimalist", "Unisex"],
    ),
    # ── Necklaces ───────────────────────────────────────────────────────────
    models.ProductCreate(
        name="Gold Pendant Necklace",
        price=21000, original_price=24000, discount=12.5,
        category="necklaces", sub="pendant",
        description="Classic gold pendant necklace with intricate filigree design",
        image="/images/necklaces.jpg",
        images=["/images/necklaces.jpg", "/images/necklaces-2.jpg"],
        rating=4.6, review_count=334,
        in_stock=True, stock_quantity=20, is_featured=True,
        highlights=["22K Gold", "Lightweight", "Adjustable Chain"],
    ),
    models.ProductCreate(
        name="Velvet Choker Necklace",
        price=26000, original_price=30000, discount=13.3,
        category="necklaces", sub="choker",
        description="Luxurious velvet choker with diamond accent",
        image="/images/necklaces.jpg",
        images=["/images/necklaces.jpg"],
        rating=4.9, review_count=156,
        in_stock=True, stock_quantity=12,
        highlights=["Premium Velvet", "Diamond Accent", "Party Wear"],
    ),
    models.ProductCreate(
        name="Temple Gold Necklace",
        price=42000, original_price=48000, discount=12.5,
        category="necklaces", sub="temple",
        description="Traditional temple-style gold necklace with ruby accents",
        image="/images/necklaces.jpg",
        images=["/images/necklaces.jpg"],
        rating=4.8, review_count=201,
        in_stock=True, stock_quantity=8, is_featured=True,
        highlights=["Traditional Design", "Ruby Accents", "22K Gold"],
    ),
    # ── Anklets ─────────────────────────────────────────────────────────────
    models.ProductCreate(
        name="Classic Gold Anklet",
        price=7000, original_price=8000, discount=12.5,
        category="anklets", sub="gold",
        description="Elegant classic gold anklet for everyday styling",
        image="/images/anklets.jpg",
        images=["/images/anklets.jpg"],
        rating=4.4, review_count=289,
        in_stock=True, stock_quantity=40,
        highlights=["18K Gold", "Durable", "Free Size"],
    ),
    models.ProductCreate(
        name="Beaded Silver Anklet",
        price=3500, original_price=4200, discount=16.7,
        category="anklets", sub="silver",
        description="Delicate beaded silver anklet with charm",
        image="/images/anklets.jpg",
        images=["/images/anklets.jpg"],
        rating=4.2, review_count=175,
        in_stock=True, stock_quantity=60,
        highlights=["92.5 Silver", "Lightweight", "Beach Wear"],
    ),
    # ── Bangles ─────────────────────────────────────────────────────────────
    models.ProductCreate(
        name="Traditional Kada Bangle",
        price=15000, original_price=18000, discount=16.7,
        category="bangles", sub="kada",
        description="Traditional thick gold kada bangle for festivals",
        image="/images/bangles.jpg",
        images=["/images/bangles.jpg", "/images/bangles-2.jpg"],
        rating=4.7, review_count=223,
        in_stock=True, stock_quantity=25, is_featured=True,
        highlights=["22K Gold", "Traditional Design", "Auspicious"],
    ),
    models.ProductCreate(
        name="Kundan Bangle Set",
        price=12000, original_price=14500, discount=17.2,
        category="bangles", sub="kundan",
        description="Exquisite kundan work bangle set of 4 pieces",
        image="/images/bangles.jpg",
        images=["/images/bangles.jpg"],
        rating=4.6, review_count=118,
        in_stock=True, stock_quantity=20,
        highlights=["Kundan Work", "Bridal Wear", "Set of 4"],
    ),
    # ── Earrings ────────────────────────────────────────────────────────────
    models.ProductCreate(
        name="Diamond Stud Earrings",
        price=15000, original_price=18000, discount=16.7,
        category="earrings", sub="studs",
        description="Elegant certified diamond stud earrings",
        image="/images/earrings.jpg",
        images=["/images/earrings.jpg", "/images/earrings-2.jpg"],
        rating=4.8, review_count=389,
        in_stock=True, stock_quantity=18, is_featured=True,
        highlights=["Certified Diamonds", "Screw Back", "All Occasion"],
    ),
    models.ProductCreate(
        name="Jhumka Drop Earrings",
        price=8500, original_price=10000, discount=15.0,
        category="earrings", sub="jhumka",
        description="Traditional gold jhumka earrings with pearl drops",
        image="/images/earrings.jpg",
        images=["/images/earrings.jpg"],
        rating=4.5, review_count=267,
        in_stock=True, stock_quantity=35,
        highlights=["Pearl Drops", "Traditional", "Lightweight"],
    ),
    models.ProductCreate(
        name="Hoop Earrings",
        price=5500, original_price=6500, discount=15.4,
        category="earrings", sub="hoops",
        description="Modern gold hoop earrings for everyday glam",
        image="/images/earrings.jpg",
        images=["/images/earrings.jpg"],
        rating=4.3, review_count=312,
        in_stock=True, stock_quantity=45,
        highlights=["18K Gold", "Modern", "Lightweight"],
    ),
    # ── Chains ──────────────────────────────────────────────────────────────
    models.ProductCreate(
        name="Figaro Gold Chain",
        price=18000, original_price=21000, discount=14.3,
        category="chains", sub="figaro",
        description="Classic Figaro pattern gold chain, perfect for pendants",
        image="/images/chains.jpg",
        images=["/images/chains.jpg"],
        rating=4.5, review_count=143,
        in_stock=True, stock_quantity=22,
        highlights=["22K Gold", "Hallmarked", "Unisex"],
    ),
    models.ProductCreate(
        name="Box Chain Necklace",
        price=14000, original_price=17000, discount=17.6,
        category="chains", sub="box",
        description="Sleek box-link gold chain for a minimalist look",
        image="/images/chains.jpg",
        images=["/images/chains.jpg"],
        rating=4.4, review_count=89,
        in_stock=True, stock_quantity=28,
        highlights=["18K Gold", "Minimalist", "Durable"],
    ),
]

ADMIN_EMAIL = "admin@aureliajewels.com"
ADMIN_PASSWORD = "Admin@1234"   # Change after first login!

DEMO_EMAIL = "demo@aureliajewels.com"
DEMO_PASSWORD = "Demo@1234"


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

def seed(reset: bool = False) -> None:
    if reset:
        print("🗑️  Dropping and recreating all tables…")
        from sqlmodel import SQLModel
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        print("✅ Tables recreated.")
    else:
        init_db()   # create tables if they don't exist yet

    with Session(engine) as session:

        # ── Products ─────────────────────────────────────────────────────
        existing_product = session.exec(select(models.Product)).first()
        if existing_product and not reset:
            print(f"⏭️  Products already seeded – skipping (use --reset to re-seed).")
        else:
            for p in PRODUCTS:
                db_prod = models.Product.from_orm(p)
                session.add(db_prod)
            session.commit()
            print(f"✅ Seeded {len(PRODUCTS)} products.")

        # ── Admin user ───────────────────────────────────────────────────
        admin = session.exec(
            select(models.User).where(models.User.email == ADMIN_EMAIL)
        ).first()
        if admin and not reset:
            print(f"⏭️  Admin user already exists – skipping.")
        else:
            admin = models.User(
                email=ADMIN_EMAIL,
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                full_name="Aurelia Admin",
                is_admin=True,
                is_active=True,
            )
            session.add(admin)
            session.commit()
            print(f"✅ Created admin user → {ADMIN_EMAIL}")
            print(f"   Password: {ADMIN_PASSWORD}  ← change this after first login!")

        # ── Demo / regular user ──────────────────────────────────────────
        demo = session.exec(
            select(models.User).where(models.User.email == DEMO_EMAIL)
        ).first()
        if demo and not reset:
            print(f"⏭️  Demo user already exists – skipping.")
        else:
            demo = models.User(
                email=DEMO_EMAIL,
                hashed_password=get_password_hash(DEMO_PASSWORD),
                full_name="Demo Customer",
                is_admin=False,
                is_active=True,
            )
            session.add(demo)
            session.commit()
            print(f"✅ Created demo user  → {DEMO_EMAIL}")
            print(f"   Password: {DEMO_PASSWORD}")

    print("\n✨ Database seeded successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Aurelia Jewels database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear all existing data before seeding",
    )
    args = parser.parse_args()
    seed(reset=args.reset)
