from typing import cast

from django.contrib import admin
from django.db.models import (
    Avg,
    Count,
    DecimalField,
    F,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
)
from django.db.models.functions import Coalesce
from django.http import HttpRequest

from orders.models import OrderItem
from reviews.models import Review

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )

    search_fields = (
        'name',
    )

    prepopulated_fields = {
        'slug': ('name',),
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'sold_quantity',
        'orders_count',
        'revenue',
        'avg_rating',
        'is_active',
    )

    list_filter = (
        'category',
        'is_active',
    )

    search_fields = (
        'name',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',),
    }

    list_editable = (
        'stock',
        'price',
        'is_active',
    )

    actions = [
        'activate',
        'deactivate',
    ]

    def get_queryset(
        self,
        request: HttpRequest,
    ) -> QuerySet[Product, Product]:
        """Добавляет статистику по продажам и рейтингам."""

        queryset = cast(
            QuerySet[Product, Product],
            super().get_queryset(request),
        )

        completed_statuses = [
            'paid',
            'shipped',
            'delivered',
        ]

        sold_quantity = (
            OrderItem.objects
            .filter(
                product=OuterRef('pk'),
                order__status__in=completed_statuses,
            )
            .values('product')
            .annotate(
                total=Sum('quantity'),
            )
            .values('total')
        )

        orders_count = (
            OrderItem.objects
            .filter(
                product=OuterRef('pk'),
                order__status__in=completed_statuses,
            )
            .values('product')
            .annotate(
                total=Count('order', distinct=True),
            )
            .values('total')
        )

        revenue = (
            OrderItem.objects
            .filter(
                product=OuterRef('pk'),
                order__status__in=completed_statuses,
            )
            .values('product')
            .annotate(
                total=Sum(
                    F('quantity') * F('price'),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                ),
            )
            .values('total')
        )

        avg_rating = (
            Review.objects
            .filter(product=OuterRef('pk'))
            .values('product')
            .annotate(
                average=Avg('rating'),
            )
            .values('average')
        )

        return queryset.annotate(
            _sold_quantity=Coalesce(
                Subquery(
                    sold_quantity,
                    output_field=IntegerField(),
                ),
                0,
            ),
            _orders_count=Coalesce(
                Subquery(
                    orders_count,
                    output_field=IntegerField(),
                ),
                0,
            ),
            _revenue=Coalesce(
                Subquery(
                    revenue,
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                ),
                0,
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            ),
            _avg_rating=Subquery(
                avg_rating,
                output_field=DecimalField(
                    max_digits=4,
                    decimal_places=2,
                ),
            ),
        )

    @admin.display(
        description='Продано',
        ordering='_sold_quantity',
    )
    def sold_quantity(self, obj):
        """Возвращает количество проданных единиц товара."""

        return obj._sold_quantity

    @admin.display(
        description='Заказов',
        ordering='_orders_count',
    )
    def orders_count(self, obj):
        """Возвращает количество оплаченных заказов с этим товаром."""

        return obj._orders_count

    @admin.display(
        description='Выручка',
        ordering='_revenue',
    )
    def revenue(self, obj):
        """Возвращает выручку от продажи товара."""

        return obj._revenue

    @admin.display(
        description='Рейтинг',
        ordering='_avg_rating',
    )
    def avg_rating(self, obj):
        """Возвращает средний рейтинг товара."""

        if obj._avg_rating is not None:
            return round(obj._avg_rating, 2)

        return '-'

    @admin.action(
        description='Активировать выбранные',
    )
    def activate(
        self,
        request: HttpRequest,
        queryset: QuerySet,
    ):
        """Активирует выбранные товары."""

        updated = queryset.update(is_active=True)

        self.message_user(
            request,
            f'Активировано: {updated}',
        )

    @admin.action(
        description='Снять с публикации',
    )
    def deactivate(
        self,
        request: HttpRequest,
        queryset: QuerySet,
    ):
        """Снимает с публикации."""

        updated = queryset.update(is_active=False)

        self.message_user(
            request,
            f'Снято: {updated}',
        )
