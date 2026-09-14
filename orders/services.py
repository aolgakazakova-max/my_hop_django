from django.db import transaction

from products.models import Product

from .models import Order, OrderItem


class OutOfStock(Exception):
    pass


@transaction.atomic
def create_order(user, cart, data: dict) -> Order:
    order = Order.objects.create(
        user=user,
        status=Order.Status.PAID,
        shipping_address=(
            f'{data["full_name"]}, {data["phone_number"]}\n'
            f'{data["city"]}, {data["address"]}'
        ),
    )

    total = 0

    for item in cart:
        product = Product.objects.get(pk=item["product_id"])

        if product.stock < item["quantity"]:
            raise OutOfStock(
                f'Не хватает товара "{product.name}" на складе.'
            )

        product.stock -= item["quantity"]
        product.save(update_fields=["stock"])

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item["quantity"],
            price=item["price"],
        )

        total += item["price"] * item["quantity"]

    order.total_price = total
    order.save(update_fields=["total_price"])

    return order

