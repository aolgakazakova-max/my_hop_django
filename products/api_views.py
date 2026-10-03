from django.db.models import (
    Avg,
    IntegerField,
    OuterRef,
    Subquery,
    Sum,
)
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from orders.models import OrderItem

from .filters import ProductFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    lookup_field = 'slug'

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = ['name', 'description']

    ordering_fields = [
        'price',
        'created_at',
        'avg_rating',
        'popularity',
    ]

    ordering = ['-created_at']

    def get_queryset(self):
        sold_quantity = (
            OrderItem.objects
            .filter(
                product=OuterRef('pk'),
                order__status__in=[
                    'paid',
                    'shipped',
                    'delivered',
                ],
            )
            .values('product')
            .annotate(
                total_sold=Sum('quantity')
            )
            .values('total_sold')
        )

        return (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .annotate(
                avg_rating=Avg('reviews__rating'),
                popularity=Coalesce(
                    Subquery(
                        sold_quantity,
                        output_field=IntegerField(),
                    ),
                    0,
                ),
            )
        )