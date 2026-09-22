from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from payments.services import process_payment

from .models import Order


class OutOfStock(Exception):
    """Raised when there is not enough product stock to create an order."""


@transaction.atomic
def create_order(user, cart, data):
    """
    Create an order from the current cart.

    The function checks product stock, creates the order and its items,
    processes the mock payment, decreases stock and sends notification
    emails to the customer and administrator.
    """

    total = Decimal('0.00')

    for item in cart:
        product = item['product']
        quantity = item['quantity']

        if quantity > product.stock:
            raise OutOfStock(
                f'Not enough stock for {product.name}.'
            )

        total += product.price * quantity

    if total <= Decimal('0.00'):
        raise ValueError('Order total must be greater than zero.')

    payment_type = data.get(
        'payment_type',
        Order.PaymentType.DEBIT,
    )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
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

        product.stock -= quantity
        product.save(update_fields=['stock'])

        order.items.create(
            product=product,
            quantity=quantity,
            price=product.price,
        )

    payment = process_payment(order)

    subject = f'Order #{order.pk} confirmation'

    message = (
        f'Order #{order.pk}\n'
        f'Total: {order.total_price}\n'
        f'Payment status: {payment.status}\n'
        f'Payment type: {order.get_payment_type_display()}\n'
        f'Shipping address:\n{order.shipping_address}'
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    admin_email = getattr(settings, 'ADMIN_EMAIL', None)

    if admin_email:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )

    return order