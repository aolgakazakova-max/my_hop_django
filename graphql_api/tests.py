import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from orders.models import Order
from payments.models import Payment
from products.models import Category, Product
from reviews.models import Review
from users.models import Profile


class GraphQLTestCase(TestCase):
    """Tests for the GraphQL API."""

    def setUp(self):
        """Create test data."""

        self.user = User.objects.create_user(
            username='graphql_user',
            password='test-password',
            email='graphql@example.com',
        )

        self.other_user = User.objects.create_user(
            username='other_user',
            password='test-password',
            email='other@example.com',
        )

        self.category, _ = Category.objects.get_or_create(
            slug='graphql-test-hops',
            defaults={
                'name': 'GraphQL Test Hops',
            },
        )

        self.product = Product.objects.create(
            name='GraphQL Test Citra Hops',
            slug='graphql-test-citra-hops',
            description='Test hop variety for GraphQL.',
            price=Decimal('5.99'),
            stock=10,
            is_active=True,
            category=self.category,
        )

        self.second_product = Product.objects.create(
            name='GraphQL Test Mosaic Hops',
            slug='graphql-test-mosaic-hops',
            description='Another test hop variety.',
            price=Decimal('4.50'),
            stock=8,
            is_active=True,
            category=self.category,
        )

        Profile.objects.create(
            user=self.user,
            full_name='GraphQL User',
            phone='0000000000',
            city='Test City',
            address='Test Address',
        )

        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comments='Excellent test hops.',
        )

    def graphql(self, query, variables=None):
        """Send a GraphQL request and return the JSON response."""

        payload = {
            'query': query,
        }

        if variables is not None:
            payload['variables'] = variables

        response = self.client.post(
            '/graphql/',
            data=json.dumps(payload),
            content_type='application/json',
        )

        return response.json()

    def test_products_query(self):
        """Products query returns active products."""

        result = self.graphql(
            '''
            query {
                products {
                    id
                    name
                    price
                }
            }
            '''
        )

        self.assertNotIn('errors', result)

        products = result['data']['products']

        test_product = next(
            product
            for product in products
            if product['id'] == str(self.product.id)
        )

        self.assertEqual(
            test_product['name'],
            'GraphQL Test Citra Hops',
        )
        self.assertEqual(
            test_product['price'],
            '5.99',
        )

    def test_categories_query(self):
        """Categories query returns the test category."""

        result = self.graphql(
            '''
            query {
                categories {
                    id
                    name
                    slug
                }
            }
            '''
        )

        self.assertNotIn('errors', result)

        categories = result['data']['categories']

        test_category = next(
            category
            for category in categories
            if category['slug'] == 'graphql-test-hops'
        )

        self.assertEqual(
            test_category['name'],
            'GraphQL Test Hops',
        )

    def test_reviews_query(self):
        """Reviews query returns product reviews."""

        result = self.graphql(
            '''
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
            '''
        )

        self.assertNotIn('errors', result)

        reviews = result['data']['reviews']

        test_review = next(
            review
            for review in reviews
            if review['id'] == str(self.review.id)
        )

        self.assertEqual(
            test_review['rating'],
            5,
        )
        self.assertEqual(
            test_review['comments'],
            'Excellent test hops.',
        )
        self.assertEqual(
            test_review['product']['name'],
            'GraphQL Test Citra Hops',
        )

    def test_profile_query_for_authenticated_user(self):
        """Profile query returns the current user's profile."""

        self.client.force_login(self.user)

        result = self.graphql(
            '''
            query {
                profile {
                    id
                    fullName
                    phone
                    city
                    address
                }
            }
            '''
        )

        self.assertNotIn('errors', result)

        profile = result['data']['profile']

        self.assertIsNotNone(profile)
        self.assertEqual(
            profile['fullName'],
            'GraphQL User',
        )
        self.assertEqual(
            profile['phone'],
            '0000000000',
        )
        self.assertEqual(
            profile['city'],
            'Test City',
        )
        self.assertEqual(
            profile['address'],
            'Test Address',
        )

    def test_profile_query_for_anonymous_user(self):
        """Profile query returns null for an anonymous user."""

        result = self.graphql(
            '''
            query {
                profile {
                    id
                    fullName
                }
            }
            '''
        )

        self.assertNotIn('errors', result)
        self.assertIsNone(
            result['data']['profile'],
        )

    def test_orders_query_returns_only_current_user_orders(self):
        """Orders query returns only the current user's orders."""

        user_order = Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('5.99'),
            shipping_address='User address',
        )

        user_order.items.create(
            product=self.product,
            quantity=1,
            price=Decimal('5.99'),
        )

        other_order = Order.objects.create(
            user=self.other_user,
            status=Order.Status.PAID,
            payment_type=Order.PaymentType.DEBIT,
            total_price=Decimal('4.50'),
            shipping_address='Other address',
        )

        other_order.items.create(
            product=self.second_product,
            quantity=1,
            price=Decimal('4.50'),
        )

        self.client.force_login(self.user)

        result = self.graphql(
            '''
            query {
                orders {
                    id
                    totalPrice
                    items {
                        quantity
                        price
                        product {
                            id
                            name
                        }
                    }
                }
            }
            '''
        )

        self.assertNotIn('errors', result)

        orders = result['data']['orders']

        self.assertEqual(
            len(orders),
            1,
        )
        self.assertEqual(
            orders[0]['id'],
            str(user_order.id),
        )
        self.assertEqual(
            orders[0]['totalPrice'],
            '5.99',
        )
        self.assertEqual(
            orders[0]['items'][0]['product']['name'],
            'GraphQL Test Citra Hops',
        )

    def test_orders_query_for_anonymous_user(self):
        """Orders query returns an empty list for an anonymous user."""

        result = self.graphql(
            '''
            query {
                orders {
                    id
                }
            }
            '''
        )

        self.assertNotIn('errors', result)
        self.assertEqual(
            result['data']['orders'],
            [],
        )

    def test_cart_mutations(self):
        """Add, update and remove cart mutations work."""

        self.client.force_login(self.user)

        add_result = self.graphql(
            '''
            mutation (
                $productId: Int!,
                $quantity: Int!
            ) {
                addToCart(
                    productId: $productId,
                    quantity: $quantity
                ) {
                    totalPrice
                    items {
                        quantity
                        totalPrice
                        product {
                            id
                            name
                        }
                    }
                }
            }
            ''',
            variables={
                'productId': self.product.pk,
                'quantity': 2,
            },
        )

        self.assertNotIn('errors', add_result)

        add_cart = add_result['data']['addToCart']

        self.assertEqual(
            add_cart['totalPrice'],
            '11.98',
        )
        self.assertEqual(
            len(add_cart['items']),
            1,
        )
        self.assertEqual(
            add_cart['items'][0]['quantity'],
            2,
        )

        update_result = self.graphql(
            '''
            mutation (
                $productId: Int!,
                $quantity: Int!
            ) {
                updateCart(
                    productId: $productId,
                    quantity: $quantity
                ) {
                    totalPrice
                    items {
                        quantity
                        totalPrice
                        product {
                            id
                            name
                        }
                    }
                }
            }
            ''',
            variables={
                'productId': self.product.pk,
                'quantity': 3,
            },
        )

        self.assertNotIn('errors', update_result)

        update_cart = update_result['data']['updateCart']

        self.assertEqual(
            update_cart['totalPrice'],
            '17.97',
        )
        self.assertEqual(
            update_cart['items'][0]['quantity'],
            3,
        )
        self.assertEqual(
            update_cart['items'][0]['totalPrice'],
            '17.97',
        )

        remove_result = self.graphql(
            '''
            mutation ($productId: Int!) {
                removeFromCart(productId: $productId) {
                    totalPrice
                    items {
                        quantity
                        totalPrice
                        product {
                            id
                            name
                        }
                    }
                }
            }
            ''',
            variables={
                'productId': self.product.pk,
            },
        )

        self.assertNotIn('errors', remove_result)

        remove_cart = remove_result['data']['removeFromCart']

        self.assertEqual(
            remove_cart['totalPrice'],
            '0.00',
        )
        self.assertEqual(
            remove_cart['items'],
            [],
        )

    def test_cart_query(self):
        """Cart query returns the current session cart."""

        self.client.force_login(self.user)

        self.graphql(
            '''
            mutation (
                $productId: Int!,
                $quantity: Int!
            ) {
                addToCart(
                    productId: $productId,
                    quantity: $quantity
                ) {
                    totalPrice
                }
            }
            ''',
            variables={
                'productId': self.second_product.pk,
                'quantity': 2,
            },
        )

        result = self.graphql(
            '''
            query {
                cart {
                    totalPrice
                    items {
                        quantity
                        totalPrice
                        product {
                            id
                            name
                            price
                        }
                    }
                }
            }
            '''
        )

        self.assertNotIn('errors', result)

        cart = result['data']['cart']

        self.assertEqual(
            cart['totalPrice'],
            '9.00',
        )
        self.assertEqual(
            len(cart['items']),
            1,
        )
        self.assertEqual(
            cart['items'][0]['quantity'],
            2,
        )
        self.assertEqual(
            cart['items'][0]['totalPrice'],
            '9.00',
        )
        self.assertEqual(
            cart['items'][0]['product']['name'],
            'GraphQL Test Mosaic Hops',
        )

    @patch('orders.services.send_mail')
    def test_create_order(self, mock_send_mail):
        """Create order mutation creates an order and clears the cart."""

        self.client.force_login(self.user)

        add_result = self.graphql(
            '''
            mutation (
                $productId: Int!,
                $quantity: Int!
            ) {
                addToCart(
                    productId: $productId,
                    quantity: $quantity
                ) {
                    totalPrice
                }
            }
            ''',
            variables={
                'productId': self.product.pk,
                'quantity': 1,
            },
        )

        self.assertNotIn('errors', add_result)
        self.assertEqual(
            add_result['data']['addToCart']['totalPrice'],
            '5.99',
        )

        result = self.graphql(
            '''
            mutation ($input: CreateOrderInput!) {
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
                            id
                            name
                        }
                    }
                }
            }
            ''',
            variables={
                'input': {
                    'fullName': 'GraphQL User',
                    'phoneNumber': '0000000000',
                    'city': 'Test City',
                    'address': 'Test Address',
                    'paymentType': 'debit',
                },
            },
        )

        self.assertNotIn('errors', result)

        order_data = result['data']['createOrder']

        self.assertEqual(
            order_data['status'],
            'paid',
        )
        self.assertEqual(
            order_data['paymentType'],
            'debit',
        )
        self.assertEqual(
            order_data['totalPrice'],
            '5.99',
        )
        self.assertEqual(
            order_data['shippingAddress'],
            'GraphQL User, 0000000000\n'
            'Test City, Test Address',
        )

        self.assertEqual(
            len(order_data['items']),
            1,
        )
        self.assertEqual(
            order_data['items'][0]['quantity'],
            1,
        )
        self.assertEqual(
            order_data['items'][0]['price'],
            '5.99',
        )
        self.assertEqual(
            order_data['items'][0]['product']['name'],
            'GraphQL Test Citra Hops',
        )

        order = Order.objects.get(
            pk=order_data['id'],
        )

        self.assertEqual(
            order.status,
            Order.Status.PAID,
        )
        self.assertEqual(
            order.total_price,
            Decimal('5.99'),
        )

        product = Product.objects.get(
            pk=self.product.pk,
        )

        self.assertEqual(
            product.stock,
            9,
        )

        payment = Payment.objects.get(
            order=order,
        )

        self.assertEqual(
            payment.amount,
            Decimal('5.99'),
        )
        self.assertEqual(
            payment.status,
            Payment.Status.PAID,
        )

        mock_send_mail.assert_called()

        cart_result = self.graphql(
            '''
            query {
                cart {
                    totalPrice
                    items {
                        quantity
                    }
                }
            }
            '''
        )

        self.assertNotIn('errors', cart_result)
        self.assertEqual(
            cart_result['data']['cart']['totalPrice'],
            '0.00',
        )
        self.assertEqual(
            cart_result['data']['cart']['items'],
            [],
        )