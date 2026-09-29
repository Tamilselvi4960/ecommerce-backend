from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .auth_views import LoginView, RegisterView

from .order_views import (
    CheckoutView,
    OrderDetailView,
    OrderListView,
)

from .views import (
    CartItemCreateView,
    CartItemDeleteView,
    CartItemUpdateView,
    CartView,
    CategoryViewSet,
    ProductViewSet,
)


router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
    basename="category"
)

router.register(
    r"products",
    ProductViewSet,
    basename="product"
)


urlpatterns = [
    # Product and Category APIs
    path(
        "",
        include(router.urls)
    ),

    # Authentication
    path(
        "auth/register/",
        RegisterView.as_view(),
        name="register"
    ),

    path(
        "auth/login/",
        LoginView.as_view(),
        name="login"
    ),

    # Cart
    path(
        "cart/",
        CartView.as_view(),
        name="cart"
    ),

    path(
        "cart/items/",
        CartItemCreateView.as_view(),
        name="cart-item-create"
    ),

    path(
        "cart/items/<int:item_id>/",
        CartItemUpdateView.as_view(),
        name="cart-item-update"
    ),

    path(
        "cart/items/<int:item_id>/delete/",
        CartItemDeleteView.as_view(),
        name="cart-item-delete"
    ),

    # Orders
    path(
        "orders/",
        OrderListView.as_view(),
        name="order-list"
    ),

    path(
        "orders/<int:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail"
    ),

    # Checkout
    path(
        "orders/checkout/",
        CheckoutView.as_view(),
        name="checkout"
    ),
]