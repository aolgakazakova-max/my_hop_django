from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem

from ..models import Category, Product


User = get_user_model()


class ProductPagesTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Тестовый хмель',
            slug='test-hops',
        )

        self.product = Product.objects.create(
            name='Citra Hops',
            slug='test-citra-hops',
            description='Ideal for IPAs and Pale Ales',
            price='5.99',
            category=self.category,
            image='products/citra.jpg',
            stock=10,
        )

        self.inactive_product = Product.objects.create(
            name='Hidden Hops',
            slug='hidden-hops',
            price='1.00',
            category=self.category,
            image='products/hidden.jpg',
            is_active=False,
        )

    def test_home_uses_products_from_database(self):
        response = self.client.get(
            reverse('products:list')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(
            response,
            self.product.get_absolute_url(),
        )
        self.assertNotContains(
            response,
            self.inactive_product.name,
        )

    def test_product_detail_is_opened_by_slug(self):
        response = self.client.get(
            reverse(
                'products:detail',
                kwargs={'slug': self.product.slug},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['product'],
            self.product,
        )
        self.assertContains(
            response,
            self.product.description,
        )

    def test_inactive_product_detail_returns_404(self):
        response = self.client.get(
            self.inactive_product.get_absolute_url()
        )

        self.assertEqual(response.status_code, 404)

    def test_products_are_registered_in_admin(self):
        self.assertTrue(
            admin.site.is_registered(Product)
        )
        self.assertTrue(
            admin.site.is_registered(Category)
        )

    def test_new_product_is_in_stock_by_default(self):
        product = Product(
            name='Default stock product',
            slug='default-stock-product',
            price='1.00',
            category=self.category,
            image='products/default.jpg',
        )

        self.assertEqual(product.stock, 100)

    def test_products_are_sorted_by_popularity(self):
        popular_product = Product.objects.create(
            name='Popular Hops',
            slug='popular-hops',
            description='Very popular hops',
            price='8.99',
            category=self.category,
            image='products/popular.jpg',
            stock=20,
        )

        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

        order = Order.objects.create(
            user=user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price='44.95',
            shipping_address='Test address',
        )

        OrderItem.objects.create(
            order=order,
            product=popular_product,
            quantity=5,
            price=popular_product.price,
        )

        response = self.client.get(
            reverse('products:list'),
            {'sort': 'popular'},
        )

        self.assertEqual(response.status_code, 200)

        products = list(response.context['products'])

        self.assertEqual(
            products[0],
            popular_product,
        )

    def test_products_can_be_filtered_by_price_range(self):
        expensive_product = Product.objects.create(
            name='Expensive Hops',
            slug='expensive-hops',
            description='Premium hops',
            price='15.00',
            category=self.category,
            image='products/expensive.jpg',
            stock=10,
        )

        response = self.client.get(
            reverse('products:list'),
            {
                'min_price': '10.00',
                'max_price': '20.00',
            },
        )

        self.assertEqual(response.status_code, 200)

        products = list(response.context['products'])

        self.assertIn(
            expensive_product,
            products,
        )
        self.assertNotIn(
            self.product,
            products,
        )

    def test_products_can_be_searched_by_name_and_description(self):
        description_product = Product.objects.create(
            name='Mosaic Hops',
            slug='test-search-citrus-hops',
            description='Special citrus aroma',
            price='7.50',
            category=self.category,
            image='products/mosaic.jpg',
            stock=10,
        )

        response = self.client.get(
            reverse('products:list'),
            {'q': 'citrus'},
        )

        self.assertEqual(response.status_code, 200)

        products = list(response.context['products'])

        self.assertIn(
            description_product,
            products,
        )
        self.assertNotIn(
            self.product,
            products,
        )

    def test_product_admin_shows_sales_analytics(self):
        user = User.objects.create_user(
            username='admin-analytics-user',
            email='admin-analytics@example.com',
            password='testpass123',
        )

        paid_order = Order.objects.create(
            user=user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price='17.97',
            shipping_address='Test address',
        )

        OrderItem.objects.create(
            order=paid_order,
            product=self.product,
            quantity=3,
            price=self.product.price,
        )

        shipped_order = Order.objects.create(
            user=user,
            status=Order.Status.SHIPPED,
            payment_type=Order.PaymentType.DEBIT,
            total_price='11.98',
            shipping_address='Test address',
        )

        OrderItem.objects.create(
            order=shipped_order,
            product=self.product,
            quantity=2,
            price=self.product.price,
        )

        canceled_order = Order.objects.create(
            user=user,
            status=Order.Status.CANCELED,
            payment_type=Order.PaymentType.DEBIT,
            total_price='59.90',
            shipping_address='Test address',
        )

        OrderItem.objects.create(
            order=canceled_order,
            product=self.product,
            quantity=10,
            price=self.product.price,
        )

        product_admin = admin.site._registry[Product]
        queryset = product_admin.get_queryset(None)

        product = queryset.get(pk=self.product.pk)

        self.assertEqual(
            product._sold_quantity,
            5,
        )
        self.assertEqual(
            product._orders_count,
            2,
        )
        self.assertEqual(
            product._revenue,
            Decimal('29.95'),
        )
