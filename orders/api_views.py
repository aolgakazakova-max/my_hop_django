from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .cart import Cart
from .models import Order
from .serializers import (
    CartAddSerializer,
    CartDeleteSerializer,
    CartSerializer,
    CartUpdateSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related('items__product')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer

        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        read_serializer = OrderSerializer(
            order,
            context=self.get_serializer_context(),
        )

        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CartAPIView(APIView):

    @extend_schema(
        responses=CartSerializer,
    )
    def get(self, request):
        cart = Cart(request)

        items = []

        for item in cart:
            items.append({
                'product_id': item['product'].id,
                'product_name': item['product'].name,
                'price': item['price'],
                'quantity': item['quantity'],
                'total_price': item['total_price'],
            })

        return Response({
            'items': items,
            'total_price': cart.get_total_price(),
        })

    @extend_schema(
        request=CartAddSerializer,
    )
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'detail': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'quantity must be an integer'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity < 1:
            return Response(
                {'detail': 'quantity must be at least 1'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True,
        )

        cart = Cart(request)

        current_quantity = cart.cart.get(
            str(product.id),
            {},
        ).get('quantity', 0)

        new_quantity = current_quantity + quantity

        if new_quantity > product.stock:
            return Response(
                {'detail': 'Not enough product in stock'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart.add(
            product,
            quantity=quantity,
        )

        return Response(
            {
                'detail': 'Product added to cart',
                'product_id': product.id,
                'quantity': new_quantity,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=CartUpdateSerializer,
    )
    def patch(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id or quantity is None:
            return Response(
                {
                    'detail': 'product_id and quantity are required',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'quantity must be an integer'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity < 1:
            return Response(
                {'detail': 'quantity must be at least 1'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True,
        )

        if quantity > product.stock:
            return Response(
                {'detail': 'Not enough product in stock'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = Cart(request)

        if str(product.id) not in cart.cart:
            return Response(
                {'detail': 'Product is not in cart'},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart.add(
            product,
            quantity=quantity,
            override=True,
        )

        return Response({
            'detail': 'Cart item updated',
            'product_id': product.id,
            'quantity': quantity,
        })

    @extend_schema(
        request=CartDeleteSerializer,
    )
    def delete(self, request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response(
                {'detail': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True,
        )

        cart = Cart(request)

        if str(product.id) not in cart.cart:
            return Response(
                {'detail': 'Product is not in cart'},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart.remove(product)

        return Response({
            'detail': 'Product removed from cart',
            'product_id': product.id,
        })

