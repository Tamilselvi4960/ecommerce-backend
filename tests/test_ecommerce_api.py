import pytest

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from store.models import (
    Cart,
    CartItem,
    Category,
    Order,
    Payment,
    Product,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="TestPassword123"
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name="Test Electronics",
        description="Test category"
    )


@pytest.fixture
def product(category):
    return Product.objects.create(
        category=category,
        name="Test Mouse",
        description="Test wireless mouse",
        price=500,
        stock=10
    )


def authenticate(client, user):
    client.force_authenticate(user=user)


@pytest.mark.django_db
def test_register(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123"
        },
        format="json"
    )

    assert response.status_code == 201
    assert response.data["username"] == "newuser"
    assert "token" in response.data


@pytest.mark.django_db
def test_login(api_client, user):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "testuser",
            "password": "TestPassword123"
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data["username"] == "testuser"
    assert "token" in response.data


@pytest.mark.django_db
def test_product_list_public(api_client, product):
    response = api_client.get(
        "/api/products/"
    )

    assert response.status_code == 200
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_product_create_requires_authentication(
    api_client,
    category
):
    response = api_client.post(
        "/api/products/",
        {
            "category": category.id,
            "name": "Unauthorized Product",
            "description": "Test product",
            "price": "1000.00",
            "stock": 5
        },
        format="json"
    )

    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_product_create_authenticated(
    api_client,
    user,
    category
):
    authenticate(api_client, user)

    response = api_client.post(
        "/api/products/",
        {
            "category": category.id,
            "name": "Authenticated Product",
            "description": "Test product",
            "price": "1200.00",
            "stock": 8
        },
        format="json"
    )

    assert response.status_code == 201
    assert response.data["name"] == "Authenticated Product"


@pytest.mark.django_db
def test_add_to_cart(
    api_client,
    user,
    product
):
    authenticate(api_client, user)

    response = api_client.post(
        "/api/cart/items/",
        {
            "product": product.id,
            "quantity": 2
        },
        format="json"
    )

    assert response.status_code == 201
    assert response.data["product"] == product.id
    assert response.data["quantity"] == 2


@pytest.mark.django_db
def test_view_cart(
    api_client,
    user,
    product
):
    authenticate(api_client, user)

    cart = Cart.objects.create(
        user=user
    )

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2
    )

    response = api_client.get(
        "/api/cart/"
    )

    assert response.status_code == 200
    assert response.data["total_amount"] == 1000


@pytest.mark.django_db
def test_checkout(
    api_client,
    user,
    product
):
    authenticate(api_client, user)

    cart = Cart.objects.create(
        user=user
    )

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2
    )

    response = api_client.post(
        "/api/orders/checkout/",
        {
            "payment_method": "upi"
        },
        format="json"
    )

    assert response.status_code == 201
    assert response.data["status"] == "confirmed"
    assert response.data["total_amount"] == "1000.00"

    product.refresh_from_db()

    assert product.stock == 8

    assert Order.objects.filter(
        user=user
    ).exists()

    assert Payment.objects.filter(
        order__user=user
    ).exists()

    assert CartItem.objects.filter(
        cart=cart
    ).count() == 0


@pytest.mark.django_db
def test_order_history(
    api_client,
    user,
    product
):
    authenticate(api_client, user)

    order = Order.objects.create(
        user=user,
        total_amount=500,
        status="confirmed"
    )

    response = api_client.get(
        "/api/orders/"
    )

    assert response.status_code == 200
    assert len(response.data) >= 1
    assert response.data[0]["id"] == order.id


@pytest.mark.django_db
def test_order_detail(
    api_client,
    user
):
    authenticate(api_client, user)

    order = Order.objects.create(
        user=user,
        total_amount=500,
        status="confirmed"
    )

    response = api_client.get(
        f"/api/orders/{order.id}/"
    )

    assert response.status_code == 200
    assert response.data["id"] == order.id
    assert response.data["status"] == "confirmed"