from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product

from ..cart import Cart
from ..models import Order, OrderItem
from ..services import OutOfStock, create_order


User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Тестовый хмель',
            slug='cart-test-hops',
        )

        self.product = Product.objects.create(
            name='Citra Hops',
            slug='cart-test-citra',
            description='Test product for cart',
            price='5.99',
            category=self.category,
            image='products/citra.jpg',
            stock=10,
        )

        self.product2 = Product.objects.create(
            name='Mosaic Hops',
            slug='cart-test-mosaic',
            description='Second test product',
            price='10.00',
            category=self.category,
            image='products/mosaic.jpg',
            stock=20,
        )

    def get_cart(self):
        request = self.client.get('/').wsgi_request
        return Cart(request)

    def test_empty_cart(self):
        cart = self.get_cart()

        self.assertEqual(len(cart), 0)
        self.assertEqual(
            cart.get_total_price(),
            Decimal('0.00'),
        )

    def test_add_product_to_cart(self):
        cart = self.get_cart()

        cart.add(self.product)

        self.assertEqual(len(cart), 1)
        self.assertEqual(
            cart.cart[str(self.product.id)]['quantity'],
            1,
        )

    def test_add_product_increases_quantity(self):
        cart = self.get_cart()

        cart.add(self.product)
        cart.add(self.product, quantity=2)

        self.assertEqual(
            cart.cart[str(self.product.id)]['quantity'],
            3,
        )

    def test_override_quantity(self):
        cart = self.get_cart()

        cart.add(self.product, quantity=5)
        cart.add(
            self.product,
            quantity=2,
            override=True,
        )

        self.assertEqual(
            cart.cart[str(self.product.id)]['quantity'],
            2,
        )

    def test_cart_length_counts_different_products(self):
        cart = self.get_cart()

        cart.add(self.product, quantity=3)
        cart.add(self.product2, quantity=5)

        self.assertEqual(len(cart), 2)

    def test_cart_total_price(self):
        cart = self.get_cart()

        cart.add(self.product, quantity=2)
        cart.add(self.product2, quantity=3)

        expected_total = (
            Decimal('5.99') * 2
            + Decimal('10.00') * 3
        )

        self.assertEqual(
            cart.get_total_price(),
            expected_total,
        )

    def test_cart_iteration_returns_product_and_total(self):
        cart = self.get_cart()

        cart.add(self.product, quantity=2)

        items = list(cart)

        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0]['product'],
            self.product,
        )
        self.assertEqual(
            items[0]['quantity'],
            2,
        )
        self.assertEqual(
            items[0]['price'],
            Decimal('5.99'),
        )
        self.assertEqual(
            items[0]['total_price'],
            Decimal('11.98'),
        )

    def test_remove_product_from_cart(self):
        cart = self.get_cart()

        cart.add(self.product)
        cart.remove(self.product)

        self.assertEqual(len(cart), 0)
        self.assertNotIn(
            str(self.product.id),
            cart.cart,
        )

    def test_remove_missing_product_does_nothing(self):
        cart = self.get_cart()

        cart.remove(self.product)

        self.assertEqual(len(cart), 0)

    def test_clear_cart(self):
        cart = self.get_cart()

        cart.add(self.product)
        cart.add(self.product2)

        cart.clear()

        self.assertEqual(len(cart), 0)
        self.assertEqual(
            cart.get_total_price(),
            Decimal('0.00'),
        )

    def test_quantity_less_than_one_is_not_added(self):
        cart = self.get_cart()

        cart.add(self.product, quantity=0)
        cart.add(self.product, quantity=-1)

        self.assertEqual(len(cart), 0)


class OrderServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
        )

        self.category = Category.objects.create(
            name='Заказ хмель',
            slug='order-test-hops',
        )

        self.product = Product.objects.create(
            name='Cascade Hops',
            slug='order-test-cascade',
            description='Test product for order',
            price='7.50',
            category=self.category,
            image='products/cascade.jpg',
            stock=10,
        )

        self.product2 = Product.objects.create(
            name='Simcoe Hops',
            slug='order-test-simcoe',
            description='Second order product',
            price='12.00',
            category=self.category,
            image='products/simcoe.jpg',
            stock=20,
        )

        self.order_data = {
            'full_name': 'Test User',
            'phone_number': '+123456789',
            'city': 'Amsterdam',
            'address': 'Test Street 10',
            'payment_type': 'debit',
        }

    def get_cart(self):
        request = self.client.get('/').wsgi_request
        return Cart(request)

    @patch('orders.services.send_mail')
    def test_create_order(self, mock_send_mail):
        cart = self.get_cart()
        cart.add(self.product, quantity=2)

        order = create_order(
            user=self.user,
            cart=cart,
            data=self.order_data,
        )

        self.assertEqual(
            Order.objects.count(),
            1,
        )

        self.assertEqual(
            order.user,
            self.user,
        )

        self.assertEqual(
            order.status,
            Order.Status.PAID,
        )

        self.assertEqual(
            order.payment_type,
            Order.PaymentType.DEBIT,
        )

        self.assertEqual(
            order.total_price,
            Decimal('15.00'),
        )

        self.assertEqual(
            order.shipping_address,
            'Test User, +123456789\nAmsterdam, Test Street 10',
        )

        self.assertEqual(
            mock_send_mail.call_count,
            2,
        )

    @patch('orders.services.send_mail')
    def test_cash_on_delivery_creates_pending_order(
        self,
        mock_send_mail,
    ):
        cart = self.get_cart()
        cart.add(self.product)

        data = {
            **self.order_data,
            'payment_type': Order.PaymentType.COD,
        }

        order = create_order(
            user=self.user,
            cart=cart,
            data=data,
        )

        self.assertEqual(
            order.status,
            Order.Status.PENDING,
        )

        self.assertEqual(
            order.payment_type,
            Order.PaymentType.COD,
        )

        self.assertEqual(
            mock_send_mail.call_count,
            2,
        )

    @patch('orders.services.send_mail')
    def test_order_item_is_created(self, mock_send_mail):
        cart = self.get_cart()
        cart.add(self.product, quantity=3)

        order = create_order(
            user=self.user,
            cart=cart,
            data=self.order_data,
        )

        item = OrderItem.objects.get(order=order)

        self.assertEqual(
            item.product,
            self.product,
        )

        self.assertEqual(
            item.quantity,
            3,
        )

        self.assertEqual(
            item.price,
            Decimal('7.50'),
        )

    @patch('orders.services.send_mail')
    def test_product_stock_is_decreased(self, mock_send_mail):
        cart = self.get_cart()
        cart.add(self.product, quantity=4)

        create_order(
            user=self.user,
            cart=cart,
            data=self.order_data,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            6,
        )

    @patch('orders.services.send_mail')
    def test_order_total_with_multiple_products(
        self,
        mock_send_mail,
    ):
        cart = self.get_cart()

        cart.add(self.product, quantity=2)
        cart.add(self.product2, quantity=3)

        order = create_order(
            user=self.user,
            cart=cart,
            data=self.order_data,
        )

        expected_total = (
            Decimal('7.50') * 2
            + Decimal('12.00') * 3
        )

        self.assertEqual(
            order.total_price,
            expected_total,
        )

    @patch('orders.services.send_mail')
    def test_create_order_sends_email(
        self,
        mock_send_mail,
    ):
        cart = self.get_cart()
        cart.add(self.product)

        create_order(
            user=self.user,
            cart=cart,
            data=self.order_data,
        )

        self.assertTrue(
            mock_send_mail.called,
        )

        recipients = [
            call.kwargs['recipient_list']
            for call in mock_send_mail.call_args_list
        ]

        self.assertIn(
            ['test@example.com'],
            recipients,
        )

    def test_create_order_with_insufficient_stock(self):
        cart = self.get_cart()
        cart.add(self.product, quantity=11)

        with self.assertRaises(OutOfStock):
            create_order(
                user=self.user,
                cart=cart,
                data=self.order_data,
            )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            10,
        )

    def test_create_order_with_zero_total(self):
        cart = self.get_cart()

        with self.assertRaises(ValueError):
            create_order(
                user=self.user,
                cart=cart,
                data=self.order_data,
            )

        self.assertEqual(
            Order.objects.count(),
            0,
        )


class CheckoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='checkoutuser',
            password='checkoutpassword123',
            email='checkout@example.com',
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword123',
            email='other@example.com',
        )

        self.category = Category.objects.create(
            name='Checkout хмель',
            slug='checkout-test-hops',
        )

        self.product = Product.objects.create(
            name='Amarillo Hops',
            slug='checkout-test-amarillo',
            description='Test product for checkout',
            price='8.00',
            category=self.category,
            image='products/amarillo.jpg',
            stock=10,
        )

        self.checkout_data = {
            'full_name': 'Checkout User',
            'phone_number': '+987654321',
            'city': 'Amsterdam',
            'address': 'Checkout Street 20',
            'payment_type': Order.PaymentType.DEBIT,
        }

    def add_product_to_cart(self, quantity=1):
        response = self.client.post(
            reverse(
                'orders:cart_add',
                kwargs={
                    'product_id': self.product.id,
                },
            ),
            data={
                'quantity': quantity,
            },
        )

        self.assertRedirects(
            response,
            reverse('orders:cart_detail'),
        )

    def test_checkout_requires_login(self):
        response = self.client.get(
            reverse('orders:checkout')
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            '/users/login/',
            response.url,
        )

    def test_checkout_with_empty_cart_redirects_to_cart(self):
        self.client.login(
            username='checkoutuser',
            password='checkoutpassword123',
        )

        response = self.client.get(
            reverse('orders:checkout')
        )

        self.assertRedirects(
            response,
            reverse('orders:cart_detail'),
        )

        self.assertEqual(
            Order.objects.count(),
            0,
        )

    def test_checkout_get_with_products(self):
        self.client.login(
            username='checkoutuser',
            password='checkoutpassword123',
        )

        self.add_product_to_cart(quantity=2)

        response = self.client.get(
            reverse('orders:checkout')
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            'checkout.html',
        )

        self.assertIn(
            'form',
            response.context,
        )

    @patch('orders.services.send_mail')
    def test_checkout_post_creates_order(
        self,
        mock_send_mail,
    ):
        self.client.login(
            username='checkoutuser',
            password='checkoutpassword123',
        )

        self.add_product_to_cart(quantity=2)

        response = self.client.post(
            reverse('orders:checkout'),
            data=self.checkout_data,
        )

        order = Order.objects.get()

        self.assertRedirects(
            response,
            reverse(
                'orders:order_success',
                kwargs={
                    'order_id': order.id,
                },
            ),
        )

        self.assertEqual(
            order.user,
            self.user,
        )

        self.assertEqual(
            order.total_price,
            Decimal('16.00'),
        )

        self.assertEqual(
            order.status,
            Order.Status.PAID,
        )

        self.assertEqual(
            order.payment_type,
            Order.PaymentType.DEBIT,
        )

        self.assertEqual(
            order.items.count(),
            1,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

        self.assertEqual(
            mock_send_mail.call_count,
            2,
        )

        request = self.client.get('/').wsgi_request
        cart = Cart(request)

        self.assertEqual(
            len(cart),
            0,
        )

    @patch('orders.services.send_mail')
    def test_checkout_cash_on_delivery_creates_pending_order(
        self,
        mock_send_mail,
    ):
        self.client.login(
            username='checkoutuser',
            password='checkoutpassword123',
        )

        self.add_product_to_cart()

        data = {
            **self.checkout_data,
            'payment_type': Order.PaymentType.COD,
        }

        response = self.client.post(
            reverse('orders:checkout'),
            data=data,
        )

        order = Order.objects.get()

        self.assertRedirects(
            response,
            reverse(
                'orders:order_success',
                kwargs={
                    'order_id': order.id,
                },
            ),
        )

        self.assertEqual(
            order.status,
            Order.Status.PENDING,
        )

        self.assertEqual(
            order.payment_type,
            Order.PaymentType.COD,
        )

        self.assertEqual(
            mock_send_mail.call_count,
            2,
        )

    @patch('orders.services.send_mail')
    def test_order_success_belongs_to_current_user(
        self,
        mock_send_mail,
    ):
        self.client.login(
            username='checkoutuser',
            password='checkoutpassword123',
        )

        self.add_product_to_cart()

        self.client.post(
            reverse('orders:checkout'),
            data=self.checkout_data,
        )

        order = Order.objects.get()

        self.client.logout()

        self.client.login(
            username='otheruser',
            password='otherpassword123',
        )

        response = self.client.get(
            reverse(
                'orders:order_success',
                kwargs={
                    'order_id': order.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_cart_add_cannot_exceed_stock(self):
        self.client.login(
            username='checkoutuser',
            password='checkoutpassword123',
        )

        response = self.client.post(
            reverse(
                'orders:cart_add',
                kwargs={
                    'product_id': self.product.id,
                },
            ),
            data={
                'quantity': 11,
            },
        )

        self.assertRedirects(
            response,
            reverse(
                'products:detail',
                kwargs={
                    'slug': self.product.slug,
                },
            ),
        )

        request = self.client.get('/').wsgi_request
        cart = Cart(request)

        self.assertEqual(
            len(cart),
            0,
        )

    def test_cart_add_requires_post(self):
        response = self.client.get(
            reverse(
                'orders:cart_add',
                kwargs={
                    'product_id': self.product.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_cart_update_cannot_exceed_stock(self):
        self.client.login(
            username='checkoutuser',
            password='checkoutpassword123',
        )

        self.add_product_to_cart(quantity=2)

        response = self.client.post(
            reverse(
                'orders:cart_update',
                kwargs={
                    'product_id': self.product.id,
                },
            ),
            data={
                'quantity': 11,
            },
        )

        self.assertRedirects(
            response,
            reverse('orders:cart_detail'),
        )

        request = self.client.get('/').wsgi_request
        cart = Cart(request)

        self.assertEqual(
            cart.cart[str(self.product.id)]['quantity'],
            2,
        )