# PayFlow Store API 

A simple e-commerce backend API built with Django. It uses Redis for the shopping cart, Celery for sending emails, and Stripe to handle payments.

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

## Setup & Run

1. Navigate to the `Backend` directory and create a Python virtual environment:
```bash
cd Backend
python -m venv venv
```

2. Activate the virtual environment and install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the `Backend/` directory and configure your Stripe developer keys:
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

4. Start the Docker containers for Redis and Postgres:
```bash
docker compose up -d
```

5. Database Migrations
Run the database migrations inside the `Backend/` folder:
```bash
python manage.py migrate
```

6. Create a superuser account to access the admin panel:
```bash
python manage.py createsuperuser
```

7. Start the Django development server:
```bash
python manage.py runserver
```

In a new terminal window, activate the virtual environment and start the Celery worker process to handle background tasks (e.g., sending emails):
```bash
celery -A PayFlow_Store worker --loglevel=info -P threads
```

> **Note on Emails:** During local development, emails are printed directly to the Django server console (`EmailBackend`).
