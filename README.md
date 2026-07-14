# Food Ordering System

A multi-restaurant food ordering platform built from a real local problem: long wait times at a pizza café in my hometown. Customers order online, restaurant owners manage their menu and orders, and the platform takes a  commission per order — similar in spirit to Swiggy/Zomato, built from scratch to understand every layer of a real production system.

## Why this project

I noticed people in my town waiting 20+ minutes just to place an order at a local pizza café with no way to pre-order. This project solves that directly, while giving me a real, defensible full-stack project to learn industry-grade backend engineering, database design, and system architecture.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** MySQL + SQLAlchemy ORM
- **Auth:** JWT (python-jose) + bcrypt password hashing
- **Frontend:** React *(planned)*
- **Caching:** Redis *(planned)*
- **Background jobs:** Celery *(planned)*
- **Deployment:** Render / Vercel / Railway *(planned)*

## Architecture

Built as a **modular monolith** — a single FastAPI application organized into isolated domain modules (`auth`, `restaurants`, `menu`, `orders`), rather than microservices. This was a deliberate design decision: microservices add network-call complexity, distributed transaction handling, and service-discovery overhead that isn't justified at this project's current scale. Each module is cleanly separated internally, making a future split into real services straightforward if ever needed.

## Key Design Decisions

- **Single `users` table with a role enum** (`customer`, `restaurant_owner`, `admin`) instead of separate tables per role — simpler auth, easier to extend with new roles later.
- **Role-based ownership checks** — a `restaurant_owner` can only modify their own restaurant's data, verified by comparing `restaurant.owner_id` against the authenticated user's ID on every write operation.
- **Price snapshotting** — order line items store `price_at_order_time` rather than referencing live menu prices, so historical orders remain accurate even after a restaurant changes its prices.
- **Normalized menu schema** — menu items, size/price variants, and add-ons are stored in separate linked tables (not flattened or stored as comma-separated lists), enabling efficient queries and safe updates as the menu grows.
- **Passwords hashed with bcrypt** (via passlib) — salted and deliberately slow, protecting against brute-force and rainbow-table attacks even in the event of a full database breach.

## Features Implemented So Far

- ✅ User signup/login with hashed passwords and JWT-based authentication
- ✅ Role-based access control (customer / restaurant_owner / admin)
- ✅ Protected routes via reusable `get_current_user` dependency
- ✅ Restaurant and menu item data models
- ✅ Menu CRUD (create, read, update, delete) with size variants and add-ons, restricted to the owning restaurant's owner
- 🔲 Order placement and order history
- 🔲 Real-time order status via WebSockets
- 🔲 Restaurant owner dashboard (orders, revenue, best-sellers)
- 🔲 Admin dashboard (cross-restaurant commission tracking)
- 🔲 Redis caching for menu endpoints
- 🔲 Background jobs for commission settlement
- 🔲 Deployment

## Local Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/food-ordering-system.git
cd food-ordering-system

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME,
# JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

# Run the server
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## API Overview

| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/auth/signup` | POST | Create a new user | No |
| `/auth/login` | POST | Log in, receive JWT | No |
| `/auth/me` | GET | Get current user details | Yes |
| `/menu/items` | POST | Add a menu item (with variants) | Yes (restaurant_owner) |
| `/menu/items/{restaurant_id}` | GET | Browse a restaurant's menu | No |
| `/menu/items/{item_id}` | PUT | Update a menu item | Yes (owning restaurant_owner) |
| `/menu/items/{item_id}` | DELETE | Delete a menu item | Yes (owning restaurant_owner) |

## Roadmap

See [Features Implemented So Far](#features-implemented-so-far) above — this project is being built milestone by milestone, with each stage fully working and tested before moving to the next.

## Author

Rakesh — built as a self-directed learning project to become industry-ready as a backend/full-stack engineer.
