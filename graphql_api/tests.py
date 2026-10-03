import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.models import Order
from payments.models import Payment
from products.models import Category, Product
from reviews.models import Review
from users.models import Profile


User = get_user_model()


class GraphQLTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='graphql-user',
            email='graphql@example.com',
            password='testpass123',
        )

        self.second_user = User.objects.create_user(
            username='graphql-second-user',
            email='graphql-second@example.com',
            password='testpass123',
        )

        self.third_user = User.objects.create_user(
            username='graphql-third-user',
            email='graphql-third@example.com',
            password='testpass123',
        )

        self.category = Category.objects.get_or_create(
            slug='graphql-test-hops',
            defaults={
                'name': 'GraphQL Test Hops',
            },
        )[0]

        self.product = Product.objects.create(
            name='Citra',
            slug='graphql-citra',
            description='Citra hop beer',
            price=Decimal('5.99'),
            category=self.category,
            image='products/test/citra.jpg',
            is_active=True,
            stock=10,
        )

        self.second_product = Product.objects.create(
            name='Mosaic',
            slug='graphql-mosaic',
            description='Mosaic hop beer',
            price=Decimal('8.99'),
            category=self.category,
            image='products/test/mosaic.jpg',
            is_active=True,
            stock=8,
        )

        self.third_product = Product.objects.create(
            name='Cascade',
            slug='graphql-cascade',
            description='Cascade hop beer',
            price=Decimal('7.50'),
            category=self.category,
            image='products/test/cascade.jpg',
            is_active=True,
            stock=15,
        )

        self.profile = Profile.objects.get_or_create(
            user=self.user,
        )[0]

        self.profile.full_name = 'GraphQL User'
        self.profile.phone = '+123456789'
        self.profile.city = 'Test City'
        self.profile.address = 'Test Address'
        self.profile.save()

        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comments='Excellent beer!',
        )

    def graphql(self, query, variables=None):
        response = self.client.post(
            '/graphql/',
            data=json.dumps(
                {
                    'query': query,
                    'variables': variables or {},
                }
            ),
            content_type='application/json',
        )

        return response

    def test_products_query(self):
        query = """
        query {
            products {
                id
                name
                slug
                description
                price
                stock
                isActive
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        products = data['data']['products']

        names = {
            product['name']
            for product in products
        }

        self.assertIn('Citra', names)
        self.assertIn('Mosaic', names)

    def test_categories_query(self):
        query = """
        query {
            categories {
                id
                name
                slug
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        categories = data['data']['categories']

        self.assertTrue(
            any(
                category['slug'] == 'graphql-test-hops'
                for category in categories
            )
        )

    def test_reviews_query(self):
        query = """
        query {
            reviews {
                id
                rating
                comments
                product {
                    id
                    name
                }
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        reviews = data['data']['reviews']

        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['rating'], 5)
        self.assertEqual(
            reviews[0]['comments'],
            'Excellent beer!',
        )
        self.assertEqual(
            reviews[0]['product']['name'],
            'Citra',
        )

    def test_profile_query_authenticated(self):
        self.client.force_login(self.user)

        query = """
        query {
            profile {
                id
                fullName
                phone
                city
                address
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        profile = data['data']['profile']

        self.assertIsNotNone(profile)
        self.assertEqual(
            profile['fullName'],
            'GraphQL User',
        )
        self.assertEqual(
            profile['city'],
            'Test City',
        )

    def test_profile_query_anonymous(self):
        query = """
        query {
            profile {
                id
                fullName
                phone
                city
                address
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)
        self.assertIsNone(data['data']['profile'])

    def test_orders_query_authenticated(self):
        order = Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('11.98'),
            shipping_address='Test Address',
        )

        order.items.create(
            product=self.product,
            quantity=2,
            price=self.product.price,
        )

        self.client.force_login(self.user)

        query = """
        query {
            orders {
                id
                status
                paymentType
                totalPrice
                shippingAddress
                items {
                    quantity
                    price
                    product {
                        name
                    }
                }
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        orders = data['data']['orders']

        self.assertEqual(len(orders), 1)
        self.assertEqual(
            orders[0]['status'],
            'paid',
        )
        self.assertEqual(
            Decimal(orders[0]['totalPrice']),
            Decimal('11.98'),
        )
        self.assertEqual(
            orders[0]['shippingAddress'],
            'Test Address',
        )
        self.assertEqual(
            orders[0]['items'][0]['quantity'],
            2,
        )
        self.assertEqual(
            orders[0]['items'][0]['product']['name'],
            'Citra',
        )

    def test_orders_query_anonymous(self):
        query = """
        query {
            orders {
                id
                status
                totalPrice
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)
        self.assertEqual(
            data['data']['orders'],
            [],
        )

    def test_cart_mutations(self):
        self.client.force_login(self.user)

        add_query = """
        mutation AddToCart($productId: Int!, $quantity: Int!) {
            addToCart(
                productId: $productId
                quantity: $quantity
            ) {
                items {
                    product {
                        id
                        name
                    }
                    quantity
                    totalPrice
                }
                totalPrice
            }
        }
        """

        response = self.graphql(
            add_query,
            {
                'productId': self.product.pk,
                'quantity': 2,
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        cart = data['data']['addToCart']

        self.assertEqual(
            cart['items'][0]['quantity'],
            2,
        )
        self.assertEqual(
            Decimal(cart['totalPrice']),
            Decimal('11.98'),
        )

        update_query = """
        mutation UpdateCart($productId: Int!, $quantity: Int!) {
            updateCart(
                productId: $productId
                quantity: $quantity
            ) {
                items {
                    product {
                        name
                    }
                    quantity
                    totalPrice
                }
                totalPrice
            }
        }
        """

        response = self.graphql(
            update_query,
            {
                'productId': self.product.pk,
                'quantity': 3,
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        cart = data['data']['updateCart']

        self.assertEqual(
            cart['items'][0]['quantity'],
            3,
        )
        self.assertEqual(
            Decimal(cart['totalPrice']),
            Decimal('17.97'),
        )

        remove_query = """
        mutation RemoveFromCart($productId: Int!) {
            removeFromCart(productId: $productId) {
                items {
                    product {
                        name
                    }
                    quantity
                }
                totalPrice
            }
        }
        """

        response = self.graphql(
            remove_query,
            {
                'productId': self.product.pk,
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        cart = data['data']['removeFromCart']

        self.assertEqual(
            cart['items'],
            [],
        )
        self.assertEqual(
            Decimal(cart['totalPrice']),
            Decimal('0.00'),
        )

    def test_cart_query(self):
        self.client.force_login(self.user)

        add_query = """
        mutation {
            addToCart(
                productId: %d
                quantity: 2
            ) {
                totalPrice
            }
        }
        """ % self.product.pk

        response = self.graphql(add_query)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            'errors',
            response.json(),
        )

        query = """
        query {
            cart {
                items {
                    product {
                        id
                        name
                    }
                    quantity
                    totalPrice
                }
                totalPrice
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        cart = data['data']['cart']

        self.assertEqual(
            len(cart['items']),
            1,
        )
        self.assertEqual(
            cart['items'][0]['quantity'],
            2,
        )
        self.assertEqual(
            cart['items'][0]['product']['name'],
            'Citra',
        )
        self.assertEqual(
            Decimal(cart['totalPrice']),
            Decimal('11.98'),
        )

    @patch('orders.services.send_mail')
    def test_create_order_mutation(self, mock_send_mail):
        self.client.force_login(self.user)

        add_query = """
        mutation {
            addToCart(
                productId: %d
                quantity: 2
            ) {
                totalPrice
            }
        }
        """ % self.product.pk

        response = self.graphql(add_query)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            'errors',
            response.json(),
        )

        mutation = """
        mutation CreateOrder($input: CreateOrderInput!) {
            createOrder(input: $input) {
                id
                status
                paymentType
                totalPrice
                shippingAddress
                items {
                    quantity
                    price
                    product {
                        name
                    }
                }
            }
        }
        """

        variables = {
            'input': {
                'fullName': 'GraphQL Customer',
                'phoneNumber': '+111111111',
                'city': 'Test City',
                'address': 'Test Street 10',
                'paymentType': 'debit',
            }
        }

        response = self.graphql(
            mutation,
            variables,
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        order_data = data['data']['createOrder']

        self.assertEqual(
            Decimal(order_data['totalPrice']),
            Decimal('11.98'),
        )
        self.assertEqual(
            order_data['shippingAddress'],
            'GraphQL Customer, +111111111\n'
            'Test City, Test Street 10',
        )
        self.assertEqual(
            order_data['items'][0]['quantity'],
            2,
        )
        self.assertEqual(
            order_data['items'][0]['product']['name'],
            'Citra',
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

        self.assertEqual(
            Order.objects.filter(
                user=self.user,
            ).count(),
            1,
        )

        self.assertTrue(
            Payment.objects.filter(
                order__user=self.user,
            ).exists()
        )

        mock_send_mail.assert_called()

        query = """
        query {
            cart {
                items {
                    product {
                        id
                    }
                    quantity
                }
                totalPrice
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        self.assertEqual(
            data['data']['cart']['items'],
            [],
        )
        self.assertEqual(
            Decimal(data['data']['cart']['totalPrice']),
            Decimal('0.00'),
        )

    def test_order_analytics_query(self):
        paid_order = Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('17.97'),
            shipping_address='Test address',
        )

        shipped_order = Order.objects.create(
            user=self.second_user,
            status=Order.Status.SHIPPED,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('9.00'),
            shipping_address='Test address',
        )

        Order.objects.create(
            user=self.third_user,
            status=Order.Status.CANCELED,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('100.00'),
            shipping_address='Test address',
        )

        paid_order.items.create(
            product=self.product,
            quantity=3,
            price=self.product.price,
        )

        shipped_order.items.create(
            product=self.second_product,
            quantity=1,
            price=self.second_product.price,
        )

        query = """
        query {
            orderAnalytics {
                orderCount
                revenue
                averageOrderValue
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        analytics = data['data']['orderAnalytics']

        self.assertEqual(
            analytics['orderCount'],
            2,
        )
        self.assertEqual(
            analytics['revenue'],
            '26.97',
        )
        self.assertEqual(
            analytics['averageOrderValue'],
            '13.485',
        )

    def test_product_analytics_query(self):
        Product.objects.exclude(
            pk__in=[
                self.product.pk,
                self.second_product.pk,
                self.third_product.pk,
            ],
        ).update(
            is_active=False,
        )

        paid_order = Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('17.97'),
            shipping_address='Test address',
        )

        delivered_order = Order.objects.create(
            user=self.second_user,
            status=Order.Status.DELIVERED,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('9.00'),
            shipping_address='Test address',
        )

        paid_order.items.create(
            product=self.product,
            quantity=5,
            price=self.product.price,
        )

        paid_order.items.create(
            product=self.second_product,
            quantity=2,
            price=self.second_product.price,
        )

        delivered_order.items.create(
            product=self.product,
            quantity=2,
            price=self.product.price,
        )

        query = """
        query {
            productAnalytics {
                popularProducts {
                    id
                    name
                    stock
                }
                totalStock
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        analytics = data['data']['productAnalytics']

        self.assertEqual(
            analytics['totalStock'],
            33,
        )

        popular_products = analytics['popularProducts']

        self.assertEqual(
            len(popular_products),
            2,
        )

        self.assertEqual(
            popular_products[0]['name'],
            'Citra',
        )

        self.assertEqual(
            popular_products[0]['stock'],
            10,
        )

        self.assertEqual(
            popular_products[1]['name'],
            'Mosaic',
        )

    def test_user_analytics_query(self):
        Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('17.97'),
            shipping_address='Test address',
        )

        Order.objects.create(
            user=self.user,
            status=Order.Status.DELIVERED,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('9.00'),
            shipping_address='Test address',
        )

        Order.objects.create(
            user=self.second_user,
            status=Order.Status.SHIPPED,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('8.99'),
            shipping_address='Test address',
        )

        Order.objects.create(
            user=self.third_user,
            status=Order.Status.CANCELED,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('100.00'),
            shipping_address='Test address',
        )

        query = """
        query {
            userAnalytics {
                activeUsers
                repeatCustomers
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        analytics = data['data']['userAnalytics']

        self.assertEqual(
            analytics['activeUsers'],
            2,
        )
        self.assertEqual(
            analytics['repeatCustomers'],
            1,
        )

    def test_product_analytics_ignores_canceled_orders(self):
        Product.objects.exclude(
            pk__in=[
                self.product.pk,
                self.second_product.pk,
                self.third_product.pk,
            ],
        ).update(
            is_active=False,
        )

        canceled_order = Order.objects.create(
            user=self.user,
            status=Order.Status.CANCELED,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('75.00'),
            shipping_address='Test address',
        )

        canceled_order.items.create(
            product=self.product,
            quantity=10,
            price=self.product.price,
        )

        query = """
        query {
            productAnalytics {
                popularProducts {
                    id
                    name
                    stock
                }
                totalStock
            }
        }
        """

        response = self.graphql(query)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertNotIn('errors', data)

        analytics = data['data']['productAnalytics']

        self.assertEqual(
            analytics['totalStock'],
            33,
        )

        self.assertEqual(
            analytics['popularProducts'],
            [],
        )