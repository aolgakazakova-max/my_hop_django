from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.models import Order
from payments.models import Payment
from payments.services import process_payment

User = get_user_model()


class ProcessPaymentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='payment_test_user',
            password='testpass123',
        )

    def create_order(self, payment_type):
        return Order.objects.create(
            user=self.user,
            payment_type=payment_type,
            total_price=Decimal('150.00'),
            shipping_address='Test address',
        )

    def test_debit_card_creates_paid_payment(self):
        order = self.create_order(Order.PaymentType.DEBIT)

        payment = process_payment(order)

        self.assertEqual(payment.status, Payment.Status.PAID)
        self.assertEqual(payment.amount, Decimal('150.00'))
        self.assertEqual(payment.order, order)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)

    def test_wallet_card_creates_paid_payment(self):
        order = self.create_order(Order.PaymentType.WALLET)

        payment = process_payment(order)

        self.assertEqual(payment.status, Payment.Status.PAID)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)

    def test_cash_on_delivery_creates_pending_payment(self):
        order = self.create_order(Order.PaymentType.COD)

        payment = process_payment(order)

        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.amount, Decimal('150.00'))

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PENDING)

    def test_payment_is_created_for_order(self):
        order = self.create_order(Order.PaymentType.DEBIT)

        process_payment(order)

        self.assertEqual(Payment.objects.count(), 1)

        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.amount, order.total_price)

    def test_second_processing_does_not_create_duplicate_payment(self):
        order = self.create_order(Order.PaymentType.DEBIT)

        first_payment = process_payment(order)
        second_payment = process_payment(order)

        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(first_payment.pk, second_payment.pk)