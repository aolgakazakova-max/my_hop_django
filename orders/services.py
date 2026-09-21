from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from .models import Order, OrderItem


class OutOfStock(Exception):
    """Возникает, если товара недостаточно на складе."""


@transaction.atomic
def create_order(user, cart, data: dict) -> Order:
    """Создаёт заказ, уменьшает остатки и отправляет email."""

    total = cart.get_total_price()

    if total <= 0:
        raise ValueError('Нельзя создать заказ с нулевой суммой.')

    payment_type = data.get(
        'payment_type',
        Order.PaymentType.DEBIT,
    )

    if payment_type == Order.PaymentType.COD:
        status = Order.Status.PENDING
    else:
        status = Order.Status.PAID

    order = Order.objects.create(
        user=user,
        status=status,
        payment_type=payment_type,
        total_price=total,
        shipping_address=(
            f'{data["full_name"]}, {data["phone_number"]}\n'
            f'{data["city"]}, {data["address"]}'
        ),
    )

    for item in cart:
        product = item['product']
        quantity = item['quantity']
        price = product.price

        if product.stock < quantity:
            raise OutOfStock(
                f'Не хватает товара "{product.name}" на складе.'
            )

        product.stock -= quantity
        product.save(update_fields=['stock'])

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price,
        )

    payment_display = order.get_payment_type_display()

    user_email = user.email

    if user_email:
        send_mail(
            subject=f'Заказ #{order.id} успешно оформлен',
            message=(
                f'Здравствуйте, {data["full_name"]}!\n\n'
                f'Ваш заказ №{order.id} успешно оформлен.\n'
                f'Сумма заказа: {order.total_price}.\n'
                f'Способ оплаты: {payment_display}.\n'
                f'Статус: {order.get_status_display()}.\n\n'
                f'Адрес доставки:\n'
                f'{order.shipping_address}\n\n'
                f'Спасибо за покупку в Hop & Barley!'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

    admin_email = getattr(settings, 'ADMIN_EMAIL', None)

    if admin_email:
        send_mail(
            subject=f'Новый заказ #{order.id}',
            message=(
                f'Поступил новый заказ №{order.id}.\n\n'
                f'Покупатель: {data["full_name"]}\n'
                f'Email: {user.email}\n'
                f'Телефон: {data["phone_number"]}\n'
                f'Город: {data["city"]}\n'
                f'Адрес: {data["address"]}\n\n'
                f'Сумма заказа: {order.total_price}.\n'
                f'Способ оплаты: {payment_display}.\n'
                f'Статус: {order.get_status_display()}.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )

    return order

