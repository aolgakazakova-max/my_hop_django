from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from orders.models import Order, OrderItem

from ..models import Category, Product


User = get_user_model()


class ProductAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='IPA',
            slug='ipa',
        )

        self.other_category = Category.objects.create(
            name='Lager',
            slug='lager',
        )

        self.product = Product.objects.create(
            name='Citra Hops',
            slug='citra-hops-api',
            description='Citrus aroma for IPA',
            price='5.99',
            category=self.category,
            image='products/citra.jpg',
            stock=10,
        )

        self.expensive_product = Product.objects.create(
            name='Mosaic Hops',
            slug='mosaic-hops-api',
            description='Tropical and citrus aroma',
            price='15.00',
            category=self.category,
            image='products/mosaic.jpg',
            stock=10,
        )

        self.other_product = Product.objects.create(
            name='Lager Malt',
            slug='lager-malt-api',
            description='Light malt for lager',
            price='3.50',
            category=self.other_category,
            image='products/lager.jpg',
            stock=10,
        )

    def test_products_can_be_filtered_by_min_price(self):
        response = self.client.get(
            '/api/products/',
            {'min_price': '10.00'},
        )

        self.assertEqual(response.status_code, 200)

        product_names = [
            item['name']
            for item in response.data['results']
        ]

        self.assertIn(
            self.expensive_product.name,
            product_names,
        )
        self.assertNotIn(
            self.product.name,
            product_names,
        )
        self.assertNotIn(
            self.other_product.name,
            product_names,
        )

    def test_products_can_be_filtered_by_max_price(self):
        response = self.client.get(
            '/api/products/',
            {'max_price': '5.00'},
        )

        self.assertEqual(response.status_code, 200)

        product_names = [
            item['name']
            for item in response.data['results']
        ]

        self.assertIn(
            self.other_product.name,
            product_names,
        )
        self.assertNotIn(
            self.product.name,
            product_names,
        )
        self.assertNotIn(
            self.expensive_product.name,
            product_names,
        )

    def test_products_can_be_filtered_by_category(self):
        response = self.client.get(
            '/api/products/',
            {'category': 'ipa'},
        )

        self.assertEqual(response.status_code, 200)

        product_names = [
            item['name']
            for item in response.data['results']
        ]

        self.assertIn(
            self.product.name,
            product_names,
        )
        self.assertIn(
            self.expensive_product.name,
            product_names,
        )
        self.assertNotIn(
            self.other_product.name,
            product_names,
        )

    def test_products_can_be_searched(self):
        response = self.client.get(
            '/api/products/',
            {'search': 'citrus'},
        )

        self.assertEqual(response.status_code, 200)

        product_names = [
            item['name']
            for item in response.data['results']
        ]

        self.assertIn(
            self.product.name,
            product_names,
        )
        self.assertIn(
            self.expensive_product.name,
            product_names,
        )
        self.assertNotIn(
            self.other_product.name,
            product_names,
        )

    def test_products_can_be_sorted_by_price(self):
        response = self.client.get(
            '/api/products/',
            {'ordering': 'price'},
        )

        self.assertEqual(response.status_code, 200)

        prices = [
            item['price']
            for item in response.data['results']
        ]

        self.assertEqual(
            prices,
            sorted(prices),
        )

    def test_products_can_be_sorted_by_popularity(self):
        user = User.objects.create_user(
            username='api-test-user',
            email='api-test@example.com',
            password='testpass123',
        )

        order = Order.objects.create(
            user=user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price='75.00',
            shipping_address='Test address',
        )

        OrderItem.objects.create(
            order=order,
            product=self.expensive_product,
            quantity=5,
            price=self.expensive_product.price,
        )

        response = self.client.get(
            '/api/products/',
            {'ordering': '-popularity'},
        )

        self.assertEqual(response.status_code, 200)

        product_names = [
            item['name']
            for item in response.data['results']
        ]

        self.assertEqual(
            product_names[0],
            self.expensive_product.name,
        )