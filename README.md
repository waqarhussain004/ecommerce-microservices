# 🛒 E-Commerce Microservices Backend

A production-style e-commerce backend built with **FastAPI**, **PostgreSQL**, **Docker**, and a **JWT-secured API Gateway**, following a **microservices architecture** with **database-per-service** isolation.

Each domain — Users, Products, Orders, and Payments — is an independently deployable service with its own database. A single **API Gateway** is the only entry point for clients, handling authentication and routing before requests ever reach a downstream service.

---

## 📑 Table of Contents

- [Architecture](#-architecture)
- [Services](#-services)
- [Authentication](#-authentication)
- [API Gateway Routes](#-api-gateway-routes)
- [Order Flow](#-order-flow)
- [Tech Stack](#-tech-stack)
- [Docker Architecture](#-docker-architecture)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Project Goals](#-project-goals)
- [Author](#-author)

---

## 🏗️ Architecture

```
                              Client
                                │
                                ▼
                      ┌───────────────────┐
                      │    API Gateway    │
                      │       :8080       │
                      │  JWT Verification │
                      └─────────┬─────────┘
                                │
         ┌───────────────┬─────┴─────┬───────────────┐
         ▼                ▼           ▼               ▼
   ┌───────────┐   ┌───────────┐  ┌───────────┐  ┌───────────┐
   │   User    │   │  Product  │  │   Order   │  │  Payment  │
   │  Service  │   │  Service  │  │  Service  │  │  Service  │
   │   :8000   │   │   :8001   │  │   :8002   │  │   :8003   │
   └─────┬─────┘   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
         ▼               ▼              ▼              ▼
   ┌───────────┐   ┌───────────┐  ┌───────────┐  ┌───────────┐
   │  User DB  │   │Product DB │  │ Order DB  │  │Payment DB │
   └───────────┘   └───────────┘  └───────────┘  └───────────┘
```

Every service owns its data exclusively — no service reads another service's database directly. Cross-service data (e.g. product price/stock during checkout) is fetched over HTTP, with the caller's JWT forwarded for authorization.

---

## 🚀 Services

### 1. User Service — `:8000`
Handles identity and access management.
- User registration and login
- Password hashing
- JWT issuance
- Role-based access control (`user` / `admin`)
- User profile management

### 2. Product Service — `:8001`
Owns the product catalog and inventory.
- Create, read, update, delete products
- Stock reduction and stock restoration
- Admin-only write operations

### 3. Order Service — `:8002`
Owns order lifecycle and business logic.
- Create orders (multiple products per order)
- Server-side product verification and stock checks
- Server-side price lookup and total calculation
- Stock reduction on successful order
- Order status management (`pending`, `confirmed`, `completed`, `cancelled`)
- User can view only their own orders; admins can manage all orders

### 4. Payment Service — `:8003`
Owns payment records and status.
- Payment creation against an order
- Payment status tracking
- Order–payment relationship

### 5. API Gateway — `:8080`
The single public entry point for the entire system.
- Routes client requests to the correct downstream service
- Verifies JWTs before forwarding any protected request
- Enforces role-based access (e.g. admin-only routes) at the edge
- Forwards the `Authorization` header downstream for defense-in-depth
- Hides internal service hostnames/ports from clients

**Example:**
```
Client → GET /products
       → API Gateway (:8080) verifies JWT
       → forwarded internally to
       → http://ecommerce-product-service:8001/products
```

---

## 🔐 Authentication

The system uses **JWT Bearer Authentication**, issued by the User Service and verified independently at both the **Gateway** and the **downstream services** (defense in depth).

**1. Login**
```
POST /auth/login
```
Request:
```json
{
  "username": "user@example.com",
  "password": "yourpassword"
}
```
Response:
```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

**2. Authenticated requests**

Every protected request must include:
```
Authorization: Bearer JWT_TOKEN
```

**3. Verification flow**
- The **API Gateway** decodes and validates the JWT (signature + expiry) before forwarding the request. Invalid or expired tokens are rejected with `401` at the edge.
- Each **downstream service** independently re-validates the token and enforces resource-level rules (e.g. a user can only access their own orders).
- Role claims (`user` / `admin`) embedded in the JWT drive authorization decisions at both layers.

---

## 📦 API Gateway Routes

| Method | Endpoint                          | Service | Access        |
|--------|------------------------------------|---------|---------------|
| POST   | `/auth/register`                   | User    | Public        |
| POST   | `/auth/login`                      | User    | Public        |
| GET    | `/users`                           | User    | Authenticated |
| GET    | `/users/me`                        | User    | Authenticated |
| GET    | `/users/{id}`                      | User    | Authenticated |
| PUT    | `/users/{id}`                      | User    | Owner         |
| DELETE | `/users/{id}`                      | User    | Owner         |
| GET    | `/products`                        | Product | Authenticated |
| GET    | `/products/{id}`                   | Product | Authenticated |
| POST   | `/products`                        | Product | Admin         |
| PUT    | `/products/{id}`                   | Product | Admin         |
| DELETE | `/products/{id}`                   | Product | Admin         |
| PATCH  | `/products/{id}/stock`             | Product | Authenticated |
| PATCH  | `/products/{id}/restore-stock`     | Product | Authenticated |
| POST   | `/orders`                          | Order   | Authenticated |
| GET    | `/orders/my`                       | Order   | Authenticated |
| GET    | `/orders/{id}`                     | Order   | Owner / Admin |
| PATCH  | `/orders/{id}/status`              | Order   | Admin         |
| PATCH  | `/orders/{id}/cancel`              | Order   | Owner         |
| POST   | `/payments`                        | Payment | Authenticated |
| GET    | `/payments/my`                     | Payment | Authenticated |
| GET    | `/payments/{id}`                   | Payment | Owner         |

> Internal service-to-service routes (e.g. `payment-confirm`) are intentionally **not** exposed through the Gateway — they're authenticated using service credentials, not user JWTs, and are called directly between containers over the Docker network.

---

## 🔄 Order Flow

```
Client
  │
  │ POST /orders  { "items": [{ "product_id": 2, "quantity": 4 }] }
  ▼
API Gateway
  │  JWT verification
  ▼
Order Service
  │
  ├── Verify product exists         → Product Service
  ├── Check stock availability      → Product Service
  ├── Fetch current price           → Product Service
  ├── Calculate line + order totals (server-side)
  ├── Reduce product stock          → Product Service
  └── Persist order + order items
  │
  ▼
Order Database
```

Key design decisions:
- **Clients never send price, stock, `user_id`, or `total_amount`.** These are always derived server-side to prevent tampering.
- `user_id` comes exclusively from the verified JWT, never from the request body.
- The Order Service is the single source of truth for pricing at the moment of purchase — it always re-fetches current price/stock from the Product Service rather than trusting client input.

---

## 🛠️ Tech Stack

| Category            | Technology                     |
|----------------------|--------------------------------|
| Language              | Python                        |
| Framework             | FastAPI                       |
| Database              | PostgreSQL                    |
| ORM                    | SQLAlchemy                    |
| Validation             | Pydantic                      |
| Auth                   | JWT (PyJWT)                   |
| Inter-service HTTP     | HTTPX                         |
| Containerization        | Docker, Docker Compose        |
| Architecture             | Microservices, REST, API Gateway |

---

## 🐳 Docker Architecture

Each microservice runs in its own container with its own database, following the **Database-per-Service** pattern. All containers share a common Docker network so services communicate via container names instead of `localhost`.

```
Docker Compose
│
├── ecommerce-api-gateway
│
├── ecommerce-user-service
├── ecommerce-user-postgres
│
├── ecommerce-product-service
├── ecommerce-product-postgres
│
├── ecommerce-order-service
├── ecommerce-order-postgres
│
├── ecommerce-payment-service
└── ecommerce-payment-postgres
```

---

## ▶️ Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/waqarhussain004/ecommerce-microservices.git
cd ecommerce-microservices
```

**2. Configure environment variables**

Each service reads its own `.env` (database URL, `SECRET_KEY`, `ALGORITHM`, etc.). Ensure the JWT `SECRET_KEY` and `ALGORITHM` are **identical** across the User Service, Order Service, Payment Service, and the API Gateway — otherwise token verification will fail downstream.

**3. Build and start all services**
```bash
docker compose up -d --build
```

**4. Verify containers are running**
```bash
docker ps
```

### 🌐 Service URLs

| Service          | URL                          |
|-------------------|-------------------------------|
| API Gateway        | http://localhost:8080        |
| User Service        | http://localhost:8000        |
| Product Service      | http://localhost:8001        |
| Order Service         | http://localhost:8002        |
| Payment Service        | http://localhost:8003        |

> For normal client access, always go through the **API Gateway** (`:8080`). Direct service ports are exposed for local development and debugging only.

---

## 📚 API Documentation

FastAPI generates interactive Swagger docs for every service automatically.

- **API Gateway:** http://localhost:8080/docs
- Individual services are also independently browsable on their respective ports during development.

> Note: Some Gateway routes accept a raw forwarded JSON body without a typed Pydantic model, so Swagger's "Try it out" panel may not always render an input box. For those, test with `curl` or a REST client instead — the underlying request forwarding is unaffected.

---

## 🔒 Security

- JWT Bearer authentication, verified at both the Gateway and each downstream service
- Password hashing (never stored in plaintext)
- Role-based authorization (`user` / `admin`)
- Admin-only write operations on Products and Order status
- Ownership checks on Orders and Payments (users can only access their own records)
- Gateway-level JWT rejection (`401`) before a request ever reaches a downstream service
- Server-side price/stock/total calculation — client input for these fields is never trusted
- `503` responses when a downstream service is unreachable, instead of hanging or leaking internal errors

---

## 🎯 Project Goals

This project was built to demonstrate practical, production-oriented backend engineering concepts:

- Microservices architecture and service boundaries
- Database-per-service isolation
- Service-to-service communication over HTTP
- API Gateway pattern with centralized authentication
- JWT-based authentication and role-based authorization
- Distributed business logic and data consistency across services
- Inventory management and stock consistency
- Order processing with server-derived pricing
- Payment processing and order–payment relationships
- Docker-based containerization and orchestration

---

## 👨‍💻 Author

**Muhammad Waqar Hussain**

GitHub: [github.com/waqarhussain004](https://github.com/waqarhussain004)
