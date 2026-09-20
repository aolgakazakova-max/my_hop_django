from django.contrib import admin
from django.db.models import Count, QuerySet, Sum
from django.http import HttpRequest

from .models import Order, OrderItem


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product',
        'quantity',
        'price',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'status',
        'total_price',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    date_hierarchy = 'created_at'

    search_fields = (
        'id',
        'user__username',
    )

    inlines = [
        OrderItemInline,
    ]

    actions = [
        'make_shipped',
        'show_revenue',
    ]

    @admin.action(
        description='Отметить как отправленные',
    )
    def make_shipped(
        self,
        request: HttpRequest,
        queryset: QuerySet,
    ):
        """Переводит выбранные заказы в статус shipped."""

        updated = queryset.update(
            status=Order.Status.SHIPPED,
        )

        self.message_user(
            request,
            f'Отправлено заказов: {updated}',
        )

    @admin.action(
        description='Показать выручку по выбранным',
    )
    def show_revenue(
            self,
            request: HttpRequest,
            queryset: QuerySet,
    ):
        """Показывает количество заказов и общую выручку."""

        agg = queryset.aggregate(
            total=Sum('total_price'),
            count=Count('id'),
        )

        self.message_user(
            request,
            f'Заказов: {agg["count"]}. '
            f'Выручка: {agg["total"] or 0}.',
        )
