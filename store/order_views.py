from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Cart,
    Order,
    OrderItem,
    Payment,
)

from .order_serializers import OrderSerializer


# ============================================================
# CHECKOUT
# ============================================================

class CheckoutView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @transaction.atomic
    def post(self, request):
        payment_method = request.data.get("payment_method")

        allowed_methods = {
            "card",
            "upi",
            "cash",
        }

        if payment_method not in allowed_methods:
            return Response(
                {
                    "detail": (
                        "Invalid payment method. "
                        "Use card, upi, or cash."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_items = (
            cart.items
            .select_related("product")
            .select_for_update()
            .all()
        )

        if not cart_items.exists():
            return Response(
                {
                    "detail": "Your cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = Decimal("0.00")

        # Check stock before creating the order
        for cart_item in cart_items:
            product = cart_item.product

            if cart_item.quantity > product.stock:
                return Response(
                    {
                        "detail": (
                            f"Not enough stock for "
                            f"{product.name}. "
                            f"Available stock: "
                            f"{product.stock}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_amount += (
                product.price * cart_item.quantity
            )

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status="confirmed"
        )

        # Create order items and reduce stock
        for cart_item in cart_items:
            product = cart_item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=product.price
            )

            product.stock -= cart_item.quantity

            product.save(
                update_fields=[
                    "stock",
                    "updated_at"
                ]
            )

        # Create payment
        Payment.objects.create(
            order=order,
            amount=total_amount,
            payment_method=payment_method,
            status="completed"
        )

        # Clear cart
        cart.items.all().delete()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# ORDER HISTORY
# ============================================================

class OrderListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related(
                "items__product"
            )
            .select_related(
                "payment"
            )
            .order_by("-created_at")
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ============================================================
# SINGLE ORDER
# ============================================================

class OrderDetailView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects
            .filter(user=request.user)
            .prefetch_related(
                "items__product"
            )
            .select_related(
                "payment"
            ),
            id=order_id
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )