from decimal import Decimal
from typing import cast

import strawberry
import strawberry_django

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