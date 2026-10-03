from decimal import Decimal
from typing import cast

import strawberry
import strawberry_django
from django.db.models import (
    Count,
    IntegerField,
    OuterRef,
    Subquery,
    Sum,
)
from django.db.models.functions import Coalesce

from orders.cart import Cart
from orders.models import Order, OrderItem
from orders.services import OutOfStock, create_order
from products.models import Category, Product
from reviews.models import Review
from users.models import Profile


@strawberry_django.type(Category)
class CategoryType:
    id: strawberry.auto
    name: strawberry.auto
    slug: strawberry.auto


@strawberry_django.type(Product)
class ProductType:
    id: strawberry.auto
    name: strawberry.auto
    slug: strawberry.auto
    description: strawberry.auto
    price: strawberry.auto
    image: strawberry.auto
    is_active: strawberry.auto
    stock: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
    category: CategoryType


@strawberry_django.type(Profile)
class ProfileType:
    id: strawberry.auto
    full_name: strawberry.auto
    phone: strawberry.auto
    city: strawberry.auto
    address: strawberry.auto


@strawberry_django.type(Review)
class ReviewType:
    id: strawberry.auto
    rating: strawberry.auto
    comments: strawberry.auto
    created_at: strawberry.auto
    product: ProductType


@strawberry_django.type(OrderItem)
class OrderItemType:
    id: strawberry.auto
    quantity: strawberry.auto
    price: strawberry.auto
    product: ProductType


@strawberry_django.type(Order)
class OrderType:
    id: strawberry.auto
    status: strawberry.auto
    payment_type: strawberry.auto
    total_price: strawberry.auto
    shipping_address: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
    items: list[OrderItemType]


@strawberry.type
class CartItemType:
    product: ProductType
    quantity: int
    total_price: str


@strawberry.type
class CartType:
    items: list[CartItemType]
    total_price: str


@strawberry.type
class OrderAnalyticsType:
    order_count: int
    revenue: str
    average_order_value: str


@strawberry.type
class ProductAnalyticsType:
    popular_products: list[ProductType]
    total_stock: int


@strawberry.type
class UserAnalyticsType:
    active_users: int
    repeat_customers: int


@strawberry.input
class CreateOrderInput:
    full_name: str
    phone_number: str
    city: str
    address: str
    payment_type: str = Order.PaymentType.DEBIT


def get_cart_data(cart: Cart) -> CartType:
    items = [
        CartItemType(
            product=item['product'],
            quantity=item['quantity'],
            total_price=str(
                Decimal(str(item['total_price']))
            ),
        )
        for item in cart
    ]

    return CartType(
        items=items,
        total_price=str(
            Decimal(str(cart.get_total_price()))
        ),
    )


def get_completed_statuses():
    """Return order statuses included in sales analytics."""

    return [
        Order.Status.PAID,
        Order.Status.SHIPPED,
        Order.Status.DELIVERED,
    ]


@strawberry.type
class Query:

    @strawberry_django.field
    def categories(self) -> list[CategoryType]:
        return cast(
            list[CategoryType],
            Category.objects.all(),
        )

    @strawberry_django.field
    def products(self) -> list[ProductType]:
        return cast(
            list[ProductType],
            Product.objects.filter(is_active=True),
        )

    @strawberry_django.field
    def reviews(self) -> list[ReviewType]:
        return cast(
            list[ReviewType],
            Review.objects.all(),
        )

    @strawberry.field
    def profile(
        self,
        info: strawberry.Info,
    ) -> ProfileType | None:
        user = info.context.request.user

        if not user.is_authenticated:
            return None

        profile = Profile.objects.filter(user=user).first()

        return cast(
            ProfileType | None,
            profile,
        )

    @strawberry.field
    def orders(
        self,
        info: strawberry.Info,
    ) -> list[OrderType]:
        user = info.context.request.user

        if not user.is_authenticated:
            return []

        orders = (
            Order.objects
            .filter(user=user)
            .prefetch_related('items__product')
        )

        return cast(
            list[OrderType],
            orders,
        )

    @strawberry.field
    def cart(
        self,
        info: strawberry.Info,
    ) -> CartType:
        cart = Cart(info.context.request)

        return get_cart_data(cart)

    @strawberry.field
    def order_analytics(self) -> OrderAnalyticsType:
        """Return analytics for completed orders."""

        completed_statuses = get_completed_statuses()

        completed_orders = Order.objects.filter(
            status__in=completed_statuses,
        )

        order_count = completed_orders.count()

        revenue = completed_orders.aggregate(
            total=Sum('total_price'),
        )['total'] or Decimal('0.00')

        if order_count:
            average_order_value = (
                revenue / order_count
            )
        else:
            average_order_value = Decimal('0.00')

        return OrderAnalyticsType(
            order_count=order_count,
            revenue=str(
                revenue.quantize(Decimal('0.01'))
            ),
            average_order_value=str(
                average_order_value.quantize(
                    Decimal('0.001')
                )
            ),
        )

    @strawberry.field
    def product_analytics(self) -> ProductAnalyticsType:
        """Return product sales and stock analytics."""

        completed_statuses = get_completed_statuses()

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

        products = (
            Product.objects
            .filter(is_active=True)
            .annotate(
                sold_quantity=Coalesce(
                    Subquery(
                        sold_quantity,
                        output_field=IntegerField(),
                    ),
                    0,
                ),
            )
            .order_by(
                '-sold_quantity',
                'id',
            )
        )

        total_stock = (
            Product.objects
            .filter(is_active=True)
            .aggregate(
                total=Sum('stock'),
            )['total'] or 0
        )

        popular_products = [
            cast(ProductType, product)
            for product in products
            if product.sold_quantity > 0
        ]

        return ProductAnalyticsType(
            popular_products=popular_products,
            total_stock=total_stock,
        )

    @strawberry.field
    def user_analytics(self) -> UserAnalyticsType:
        """Return customer activity analytics."""

        completed_statuses = get_completed_statuses()

        completed_orders = Order.objects.filter(
            status__in=completed_statuses,
        )

        active_users = (
            completed_orders
            .values('user')
            .distinct()
            .count()
        )

        repeat_customers = (
            completed_orders
            .values('user')
            .annotate(
                order_count=Count('id'),
            )
            .filter(order_count__gt=1)
            .count()
        )

        return UserAnalyticsType(
            active_users=active_users,
            repeat_customers=repeat_customers,
        )


@strawberry.type
class Mutation:

    @strawberry.field
    def add_to_cart(
        self,
        info: strawberry.Info,
        product_id: int,
        quantity: int = 1,
    ) -> CartType:
        product = Product.objects.get(
            id=product_id,
            is_active=True,
        )

        cart = Cart(info.context.request)

        cart.add(
            product,
            quantity,
        )

        return get_cart_data(cart)

    @strawberry.field
    def update_cart(
        self,
        info: strawberry.Info,
        product_id: int,
        quantity: int,
    ) -> CartType:
        product = Product.objects.get(
            id=product_id,
            is_active=True,
        )

        cart = Cart(info.context.request)

        cart.update(
            product,
            quantity,
        )

        return get_cart_data(cart)

    @strawberry.field
    def remove_from_cart(
        self,
        info: strawberry.Info,
        product_id: int,
    ) -> CartType:
        product = Product.objects.get(
            id=product_id,
            is_active=True,
        )

        cart = Cart(info.context.request)

        cart.remove(product)

        return get_cart_data(cart)

    @strawberry.field
    def create_order(
        self,
        info: strawberry.Info,
        input: CreateOrderInput,
    ) -> OrderType:
        user = info.context.request.user

        if not user.is_authenticated:
            raise ValueError(
                'Authentication is required to create an order.'
            )

        cart = Cart(info.context.request)

        if len(cart) == 0:
            raise ValueError('Cart is empty.')

        payment_types = {
            choice[0]
            for choice in Order.PaymentType.choices
        }

        if input.payment_type not in payment_types:
            raise ValueError(
                'Invalid payment type.'
            )

        data = {
            'full_name': input.full_name,
            'phone_number': input.phone_number,
            'city': input.city,
            'address': input.address,
            'payment_type': input.payment_type,
        }

        try:
            order = create_order(
                user=user,
                cart=cart,
                data=data,
            )
        except OutOfStock as error:
            raise ValueError(str(error)) from error

        cart.clear()

        return cast(
            OrderType,
            Order.objects
            .prefetch_related('items__product')
            .get(pk=order.pk),
        )


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)