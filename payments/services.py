from orders.models import Order

from .models import Payment


def process_payment(order: Order) -> Payment:
    """
    Создаёт и обрабатывает моковый платёж для заказа.
    """

    if order.payment_type == Order.PaymentType.COD:
        status = Payment.Status.PENDING
    else:
        status = Payment.Status.PAID

    payment, _ = Payment.objects.update_or_create(
        order=order,
        defaults={
            'amount': order.total_price,
            'status': status,
        },
    )

    if status == Payment.Status.PAID:
        order.status = Order.Status.PAID
        order.save(update_fields=['status', 'updated_at'])
    else:
        order.status = Order.Status.PENDING
        order.save(update_fields=['status', 'updated_at'])

    return payment