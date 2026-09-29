# E-Commerce Backend

A backend e-commerce application built using Django, Django REST Framework, and PostgreSQL.

## Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- psycopg2
- django-filter
- Token Authentication
- pytest
- pytest-django

## Features

### Authentication

- User registration
- User login
- Token authentication
- Authenticated user permissions

### Products

- Create product
- List products
- View product details
- Update product
- Delete product
- Search products
- Filter products by category
- Order products by price, name, stock, or creation date

### Categories

- Create category
- List categories
- View category details
- Update category
- Delete category
- Search categories

### Cart

- Create user cart
- Add product to cart
- Update cart item quantity
- Remove cart item
- Calculate cart subtotal
- Calculate cart total
- Stock validation

### Checkout

- Validate cart
- Validate product stock
- Create order
- Create order items
- Reduce product stock
- Create payment
- Clear cart after checkout
- Database transaction support

### Orders

- Order history
- View individual order
- Order status
- Payment information

## API Endpoints

### Authentication

```text
POST /api/auth/register/
POST /api/auth/login/