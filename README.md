# PayFlow Store API 

A simple e-commerce backend API built with Django. It uses Redis for the shopping cart, Celery for sending emails, and Stripe to handle payments.

---

## Running Tests

The project includes a robust suite of automated tests covering the cart logic, order creation, and webhook security. To execute the tests inside the Docker container, run:

```bash
docker compose exec web python manage.py test
```

---

## API Endpoints

### Auth
* `POST /api/token/` - Get access/refresh tokens.
* `POST /api/token/refresh/` - Refresh access token.

### Products
* `GET /api/products/` - List all products.
* `GET /api/products/<id>/` - Get product details.

### Cart
* `GET /api/orders/cart/` - View cart.
* `POST /api/orders/cart/` - Add item to cart (`product_id`, `quantity`).
* `DELETE /api/orders/cart/` - Remove item from cart (`product_id`).

### Orders & Payments
* `POST /api/orders/create/` - Create order and get Stripe Checkout URL.
* `POST /api/orders/webhook/` - Stripe webhook to process paid orders.

### Docs
* `GET /api/docs/` - Swagger UI.
* `GET /api/schema/` - OpenAPI schema.

---

## Setup & Run (Docker Workflow)

The entire application runs inside Docker (Django, Celery, Redis, and Postgres).

1. **Set up Environment Variables:**
Navigate to the `Backend` directory and copy the `.env.example` to `.env`:
```bash
cp Backend/.env.example Backend/.env
```
Update the keys in `Backend/.env`:
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

2. **Start the Application:**
Run the following command in the root directory (where `docker-compose.yml` is located) to build and start all services:
```bash
docker compose up --build
```

3. **Database Setup:**
While the containers are running, open a new terminal and run migrations:
```bash
docker compose exec web python manage.py migrate
```
Create a superuser account for the admin panel:
```bash
docker compose exec web python manage.py createsuperuser
```
4. **Installing venv for IDE (optional):**
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r Backend/requirements.txt
```