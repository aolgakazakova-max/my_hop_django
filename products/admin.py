from typing import cast

from django.contrib import admin
from django.db.models import Avg, Count, QuerySet
from django.http import HttpRequest

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'orders_count',
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
        """Добавляет статистику по продажам и рейтингу."""

        queryset = cast(
            QuerySet[Product, Product],
            super().get_queryset(request),
        )

        return queryset.annotate(
            _orders_count=Count(
                'order_items',
                distinct=True,
            ),
            _avg_rating=Avg(
                'reviews__rating',
            ),
        )

    @admin.display(
        description='Продано',
        ordering='_orders_count',
    )
    def orders_count(self, obj):
        """Возвращает количество заказов с этим товаром."""

        return obj._orders_count

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