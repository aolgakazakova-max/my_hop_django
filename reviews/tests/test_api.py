from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from products.models import Category, Product

from ..forms import ReviewForm
from ..models import Review

User = get_user_model()


class ReviewAPITests(TestCase):
    """Тесты DRF API отзывов."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            password='testpass123',
        )

        self.other_user = User.objects.create_user(
            username='petr',
            password='testpass123',
        )

        self.category = Category.objects.create(
            name='Beer',
            slug='beer',
        )

        self.product = Product.objects.create(
            name='Test Beer',
            slug='test-beer',
            category=self.category,
            price=Decimal('10.00'),
            stock=10,
            is_active=True,
        )

        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comments='Очень хороший товар!',
        )

        self.purchased_order = Order.objects.create(
            user=self.other_user,
            status=Order.Status.PAID,
            total_price=self.product.price,
            shipping_address='Test address',
        )

        OrderItem.objects.create(
            order=self.purchased_order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )

    def api_url(self, suffix=''):
        """Возвращает URL API отзывов."""
        return f'/api/reviews/{suffix}'

    def test_list_reviews_is_public(self):
        """Список отзывов доступен без авторизации."""
        response = self.client.get(
            self.api_url()
        )

        self.assertEqual(response.status_code, 200)

    def test_retrieve_review_is_public(self):
        """Один отзыв доступен без авторизации."""
        response = self.client.get(
            self.api_url(f'{self.review.pk}/')
        )

        self.assertEqual(response.status_code, 200)

    def test_create_review_requires_authentication(self):
        """Создание отзыва требует авторизации."""
        response = self.client.post(
            self.api_url(),
            data={
                'product': self.product.pk,
                'rating': 4,
                'comments': 'Новый отзыв',
            },
            content_type='application/json',
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )

    def test_authenticated_user_can_create_review(self):
        """Авторизованный покупатель может создать отзыв."""
        self.client.force_login(self.other_user)

        response = self.client.post(
            self.api_url(),
            data={
                'product': self.product.pk,
                'rating': 4,
                'comments': 'Отзыв Петра',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Review.objects.filter(
                product=self.product,
                user=self.other_user,
                rating=4,
            ).exists()
        )

    def test_user_is_set_automatically_on_create(self):
        """Пользователь отзыва берётся из авторизации."""
        self.client.force_login(self.other_user)

        response = self.client.post(
            self.api_url(),
            data={
                'product': self.product.pk,
                'rating': 4,
                'comments': 'Мой отзыв',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)

        created_review = Review.objects.get(
            product=self.product,
            user=self.other_user,
        )

        self.assertEqual(
            created_review.user,
            self.other_user,
        )

    def test_user_without_purchase_cannot_create_review(self):
        """Пользователь без покупки не может создать отзыв."""
        new_user = User.objects.create_user(
            username='nopurchase',
            password='testpass123',
        )

        self.client.force_login(new_user)

        response = self.client.post(
            self.api_url(),
            data={
                'product': self.product.pk,
                'rating': 4,
                'comments': 'Отзыв без покупки',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

        self.assertFalse(
            Review.objects.filter(
                product=self.product,
                user=new_user,
            ).exists()
        )

    def test_user_cannot_update_someone_elses_review(self):
        """Пользователь не может изменить чужой отзыв."""
        self.client.force_login(self.other_user)

        response = self.client.patch(
            self.api_url(f'{self.review.pk}/'),
            data={
                'rating': 1,
                'comments': 'Изменение чужого отзыва',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

        self.review.refresh_from_db()

        self.assertEqual(self.review.rating, 5)

    def test_user_can_update_own_review(self):
        """Пользователь может изменить свой отзыв."""
        self.client.force_login(self.user)

        response = self.client.patch(
            self.api_url(f'{self.review.pk}/'),
            data={
                'rating': 4,
                'comments': 'Изменённый отзыв',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

        self.review.refresh_from_db()

        self.assertEqual(self.review.rating, 4)
        self.assertEqual(
            self.review.comments,
            'Изменённый отзыв',
        )

    def test_user_cannot_delete_someone_elses_review(self):
        """Пользователь не может удалить чужой отзыв."""
        self.client.force_login(self.other_user)

        response = self.client.delete(
            self.api_url(f'{self.review.pk}/')
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            Review.objects.filter(pk=self.review.pk).exists()
        )

    def test_user_can_delete_own_review(self):
        """Пользователь может удалить свой отзыв."""
        self.client.force_login(self.user)

        response = self.client.delete(
            self.api_url(f'{self.review.pk}/')
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Review.objects.filter(
                pk=self.review.pk
            ).exists()
        )

    def test_invalid_rating_rejected_by_api(self):
        """API отклоняет рейтинг вне диапазона 1–5."""
        self.client.force_login(self.other_user)

        response = self.client.post(
            self.api_url(),
            data={
                'product': self.product.pk,
                'rating': 6,
                'comments': 'Неверный рейтинг',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)




