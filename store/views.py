
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Cart,
    CartItem,
    Category,
    Product,
)

from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    ProductSerializer,
)


# ============================================================
# CATEGORY API
# ============================================================

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    filter_backends = [
        filters.SearchFilter,
    ]

    search_fields = [
        "name",
        "description",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]


# ============================================================
# PRODUCT API
# ============================================================

class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects
        .select_related("category")
        .all()
        .order_by("-created_at")
    )

    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "category",
    ]

    search_fields = [
        "name",
        "description",
        "category__name",
    ]

    ordering_fields = [
        "name",
        "price",
        "stock",
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]


# ============================================================
# CART API
# ============================================================

class CartView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ============================================================
# ADD ITEM TO CART
# ============================================================

class CartItemCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request):
        serializer = CartItemSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        # If product is already in cart,
        # increase its quantity.
        if existing_item:
            new_quantity = (
                existing_item.quantity + quantity
            )

            if new_quantity > product.stock:
                return Response(
                    {
                        "detail": (
                            f"Only {product.stock} "
                            "item(s) available in stock."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            existing_item.quantity = new_quantity
            existing_item.save(
                update_fields=["quantity"]
            )

            result = CartItemSerializer(
                existing_item
            )

            return Response(
                result.data,
                status=status.HTTP_200_OK
            )

        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity
        )

        result = CartItemSerializer(
            cart_item
        )

        return Response(
            result.data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# UPDATE CART ITEM
# ============================================================

class CartItemUpdateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def patch(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )

        serializer = CartItemSerializer(
            cart_item,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        updated_item = serializer.save()

        return Response(
            CartItemSerializer(
                updated_item
            ).data,
            status=status.HTTP_200_OK
        )


# ============================================================
# DELETE CART ITEM
# ============================================================

class CartItemDeleteView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def delete(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )

        cart_item.delete()

        return Response(
            {
                "message": "Cart item removed successfully."
            },
            status=status.HTTP_200_OK
        )

