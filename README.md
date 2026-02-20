# Aurelia Jewels – FastAPI Backend

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)

REST API backend for the **Aurelia Jewels** e-commerce platform, built with **FastAPI** + **SQLModel** (SQLite by default, PostgreSQL-ready for production).

---

## Features

| Area | Details |
|------|---------|
| Auth | JWT (Bearer), bcrypt password hashing, register / login / me endpoints |
| Products | CRUD + filter by category/sub/stock/featured, pagination, search, PATCH partial update |
| Cart | Per-user cart with upsert logic, enriched response with product snapshots |
| Orders | Checkout (cart → order), order history, single order detail, admin status updates |
| Admin | Role-based guard on write operations; admin order management |

---

## Quick Start

### 1. Create & activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env` and fill in your values:

```bash
copy .env .env.local   # Windows
# or
cp .env .env.local     # macOS / Linux
```

> **Important:** Generate a strong `JWT_SECRET`:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Seed the database

```bash
python scripts/seed.py           # seed (skips if data already exists)
python scripts/seed.py --reset   # wipe and re-seed
```

Default credentials created by the seed script:

| Role  | Email | Password |
|-------|-------|----------|
| Admin | admin@aureliajewels.com | Admin@1234 |
| Demo  | demo@aureliajewels.com  | Demo@1234  |

> Change these passwords after first login!

### 5. Run the development server

```bash
uvicorn main:app --reload --port 8000
# or
python main.py
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## Project Structure

```
jewellery_backend/
├── main.py               # App factory, CORS, router mounting
├── database.py           # Engine, init_db(), get_session()
├── models.py             # SQLModel table + Pydantic schemas
├── auth.py               # JWT utilities, /auth routes, dependencies
├── routers_products.py   # /products routes
├── routers_cart.py       # /cart routes
├── routers_orders.py     # /orders routes
├── scripts/
│   └── seed.py           # CLI seed script
├── requirements.txt
└── .env                  # Local config (never commit!)
```

---

## API Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | — | Create account |
| POST | /auth/login | — | Get JWT token |
| GET | /auth/me | User | Current user profile |
| GET | /products/ | — | List / filter products |
| GET | /products/search?q= | — | Keyword search |
| GET | /products/category/{cat} | — | Filter by category |
| GET | /products/{id} | — | Product detail |
| POST | /products/ | Admin | Create product |
| PUT | /products/{id} | Admin | Replace product |
| PATCH | /products/{id} | Admin | Partial update |
| DELETE | /products/{id} | Admin | Delete product |
| GET | /cart/ | User | View cart |
| POST | /cart/ | User | Add to cart (upsert) |
| PUT | /cart/{id} | User | Update quantity |
| DELETE | /cart/{id} | User | Remove item |
| DELETE | /cart/ | User | Clear cart |
| POST | /orders/ | User | Checkout |
| GET | /orders/ | User | Order history |
| GET | /orders/{id} | User | Order detail |
| GET | /orders/admin/all | Admin | All orders |
| PATCH | /orders/admin/{id}/status | Admin | Update status |

---

## Production Notes

- Set `DATABASE_URL` to PostgreSQL for production.
- Set a cryptographically strong `JWT_SECRET`.
- Set `FRONTEND_URL` to your deployed frontend domain(s).
- Run behind a reverse proxy (nginx / Caddy) with HTTPS.
