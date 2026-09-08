from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Тестовый хмель', slug='test-hops')
        cls.product = Product.objects.create(
            name='Citra Hops',
            slug='test-citra-hops',
            description='Ideal for IPAs and Pale Ales',
            price='5.99',
            category=cls.category,
            image='products/citra.jpg',
            stock=10,
        )
        cls.inactive_product = Product.objects.create(
            name='Hidden Hops',
            slug='hidden-hops',
            price='1.00',
            category=cls.category,
            image='products/hidden.jpg',
            is_active=False,
        )

    def test_home_uses_products_from_database(self):
        response = self.client.get(reverse('products:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.get_absolute_url())
        self.assertNotContains(response, self.inactive_product.name)

    def test_product_detail_is_opened_by_slug(self):
        response = self.client.get(
            reverse('products:detail', kwargs={'slug': self.product.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product)
        self.assertContains(response, self.product.description)

    def test_inactive_product_detail_returns_404(self):
        response = self.client.get(self.inactive_product.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_products_are_registered_in_admin(self):
        self.assertTrue(admin.site.is_registered(Product))
        self.assertTrue(admin.site.is_registered(Category))

    def test_new_product_is_in_stock_by_default(self):
        product = Product(
            name='Default stock product',
            slug='default-stock-product',
            price='1.00',
            category=self.category,
            image='products/default.jpg',
        )

        self.assertEqual(product.stock, 100)

# Create your tests here.
