from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product

from ..models import Order, OrderItem

User = get_user_model()


class OrderAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass123',
        )

        self.other_user = User.objects.create_user(
            username='otherapiuser',
            email='other@example.com',
            password='testpass123',
        )

        self.category = Category.objects.create(
            name='API СЃРѕР»РѕРґ',
            slug='api-hops',
        )

        self.product = Product.objects.create(
            name='API Citra',
            slug='api-citra',
            price=Decimal('8.50'),
            stock=10,
            category=self.category,
            is_active=True,
        )

        self.product2 = Product.objects.create(
            name='API Mosaic',
            slug='api-mosaic',
            price=Decimal('12.00'),
            stock=20,
            category=self.category,
            is_active=True,
        )

        self.orders_url = reverse('order-list')
        self.cart_url = reverse('cart-api')

        self.client.force_authenticate(user=self.user)

    def test_order_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.orders_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_order_list_returns_only_current_user_orders(self):
        user_order = Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            total_price=Decimal('17.00'),
            shipping_address='User address',
        )

        other_order = Order.objects.create(
            user=self.other_user,
            status=Order.Status.PAID,
            total_price=Decimal('25.00'),
            shipping_address='Other address',
        )

        response = self.client.get(self.orders_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = [
            item['id']
            for item in response.data['results']
        ]

        self.assertIn(
            user_order.id,
            returned_ids,
        )

        self.assertNotIn(
            other_order.id,
            returned_ids,
        )

    def test_order_detail_returns_current_user_order(self):
        order = Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            total_price=Decimal('17.00'),
            shipping_address='Amsterdam, Test Street 1',
        )

        response = self.client.get(
            reverse(
                'order-detail',
                args=[order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],
            order.id,
        )

    def test_order_detail_does_not_return_other_user_order(self):
        order = Order.objects.create(
            user=self.other_user,
            status=Order.Status.PAID,
            total_price=Decimal('25.00'),
            shipping_address='Other address',
        )

        response = self.client.get(
            reverse(
                'order-detail',
                args=[order.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_order(self):
        data = {
            'shipping_address': 'Amsterdam, Test Street 10',
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 2,
                },
                {
                    'product_id': self.product2.id,
                    'quantity': 1,
                },
            ],
        }

        response = self.client.post(
            self.orders_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(
            id=response.data['id'],
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
            order.total_price,
            Decimal('29.00'),
        )

        self.assertEqual(
            order.shipping_address,
            'Amsterdam, Test Street 10',
        )

        self.assertEqual(
            OrderItem.objects.filter(order=order).count(),
            2,
        )

        self.product.refresh_from_db()
        self.product2.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

        self.assertEqual(
            self.product2.stock,
            19,
        )

    def test_create_order_requires_authentication(self):
        self.client.force_authenticate(user=None)

        data = {
            'shipping_address': 'Amsterdam, Test Street 10',
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 1,
                },
            ],
        }

        response = self.client.post(
            self.orders_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_order_requires_items(self):
        data = {
            'shipping_address': 'Amsterdam, Test Street 10',
            'items': [],
        }

        response = self.client.post(
            self.orders_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            'items',
            response.data,
        )

    def test_create_order_rejects_insufficient_stock(self):
        data = {
            'shipping_address': 'Amsterdam, Test Street 10',
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': 11,
                },
            ],
        }

        response = self.client.post(
            self.orders_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
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

    def test_get_empty_cart(self):
        response = self.client.get(self.cart_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['items'],
            [],
        )

        self.assertEqual(
            Decimal(str(response.data['total_price'])),
            Decimal('0.00'),
        )

    def test_add_product_to_cart(self):
        response = self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data['product_id'],
            self.product.id,
        )

        self.assertEqual(
            response.data['quantity'],
            2,
        )

        response = self.client.get(self.cart_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['items']),
            1,
        )

        self.assertEqual(
            response.data['items'][0]['product_id'],
            self.product.id,
        )

    def test_add_product_increases_existing_quantity(self):
        self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 2,
            },
            format='json',
        )

        response = self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 3,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data['quantity'],
            5,
        )

    def test_add_product_rejects_zero_quantity(self):
        response = self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_add_product_rejects_quantity_above_stock(self):
        response = self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 11,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_add_product_rejects_inactive_product(self):
        self.product.is_active = False
        self.product.save(
            update_fields=['is_active'],
        )

        response = self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 1,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_cart_quantity(self):
        self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 2,
            },
            format='json',
        )

        response = self.client.patch(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 5,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['quantity'],
            5,
        )

    def test_update_cart_rejects_product_not_in_cart(self):
        response = self.client.patch(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 2,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_cart_rejects_quantity_above_stock(self):
        self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 2,
            },
            format='json',
        )

        response = self.client.patch(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 11,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_cart_rejects_zero_quantity(self):
        self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 2,
            },
            format='json',
        )

        response = self.client.patch(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 0,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_delete_product_from_cart(self):
        self.client.post(
            self.cart_url,
            {
                'product_id': self.product.id,
                'quantity': 2,
            },
            format='json',
        )

        response = self.client.delete(
            reverse(
                'cart-delete-api',
                args=[self.product.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.get(self.cart_url)

        self.assertEqual(
            response.data['items'],
            [],
        )

    def test_delete_product_not_in_cart_returns_404(self):
        response = self.client.delete(
            reverse(
                'cart-delete-api',
                args=[self.product.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_inactive_product_returns_404(self):
        self.product.is_active = False
        self.product.save(
            update_fields=['is_active'],
        )

        response = self.client.delete(
            reverse(
                'cart-delete-api',
                args=[self.product.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )