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


class ReviewModelTests(TestCase):
    """Тесты модели Review."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
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

    def test_create_review(self):
        """Отзыв можно создать."""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comments='Очень хороший товар!',
        )

        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comments, 'Очень хороший товар!')
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)

    def test_review_str(self):
        """__str__ возвращает ожидаемую строку."""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comments='Хорошо',
        )

        self.assertEqual(
            str(review),
            f'{self.user} -> {self.product} (4)',
        )

    def test_rating_min_validator(self):
        """Рейтинг меньше 1 не проходит валидацию."""
        review = Review(
            product=self.product,
            user=self.user,
            rating=0,
            comments='Плохо',
        )

        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_rating_max_validator(self):
        """Рейтинг больше 5 не проходит валидацию."""
        review = Review(
            product=self.product,
            user=self.user,
            rating=6,
            comments='Слишком много',
        )

        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_one_review_per_user_and_product(self):
        """Один пользователь не может оставить два отзыва на один товар."""
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comments='Первый отзыв',
        )

        duplicate_review = Review(
            product=self.product,
            user=self.user,
            rating=4,
            comments='Второй отзыв',
        )

        with self.assertRaises(ValidationError):
            duplicate_review.validate_constraints()

    def test_different_users_can_review_same_product(self):
        """Разные пользователи могут оставить отзывы на один товар."""
        second_user = User.objects.create_user(
            username='petr',
            password='testpass123',
        )

        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comments='Отзыв Ольги',
        )

        Review.objects.create(
            product=self.product,
            user=second_user,
            rating=4,
            comments='Отзыв Петра',
        )

        self.assertEqual(
            Review.objects.filter(product=self.product).count(),
            2,
        )

    def test_same_user_can_review_different_products(self):
        """Один пользователь может оставить отзывы на разные товары."""
        second_product = Product.objects.create(
            name='Second Beer',
            slug='second-beer',
            category=self.category,
            price=Decimal('12.00'),
            stock=5,
            is_active=True,
        )

        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comments='Первый товар',
        )

        Review.objects.create(
            product=second_product,
            user=self.user,
            rating=4,
            comments='Второй товар',
        )

        self.assertEqual(
            Review.objects.filter(user=self.user).count(),
            2,
        )


class ReviewFormTests(TestCase):
    """Тесты формы ReviewForm."""

    def test_valid_form(self):
        """Корректные данные проходят форму."""
        form = ReviewForm(
            data={
                'rating': 5,
                'comments': 'Отличный товар!',
            }
        )

        self.assertTrue(form.is_valid())

    def test_form_has_correct_fields(self):
        """Форма содержит rating и comments."""
        form = ReviewForm()

        self.assertEqual(
            list(form.fields.keys()),
            ['rating', 'comments'],
        )

    def test_form_rating_choices(self):
        """Форма содержит рейтинги от 1 до 5."""
        form = ReviewForm()

        choices = [
            value
            for value, label in form.fields['rating'].widget.choices
        ]

        self.assertEqual(
            choices,
            [1, 2, 3, 4, 5],
        )

    def test_form_requires_rating(self):
        """Рейтинг обязателен."""
        form = ReviewForm(
            data={
                'comments': 'Товар хороший',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)


class ReviewViewTests(TestCase):
    """Тесты обычных Django views."""

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

    def test_edit_requires_login(self):
        """Редактирование отзыва требует авторизации."""
        response = self.client.get(
            reverse(
                'reviews:edit',
                kwargs={'pk': self.review.pk},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/users/login/',
            response.url,  # type: ignore[attr-defined]
        )

    def test_delete_requires_login(self):
        """Удаление отзыва требует авторизации."""
        response = self.client.get(
            reverse(
                'reviews:delete',
                kwargs={'pk': self.review.pk},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            '/users/login/',
            response.url,  # type: ignore[attr-defined]
        )

    def test_owner_can_open_edit_page(self):
        """Владелец может открыть страницу редактирования."""
        self.client.login(
            username='olga',
            password='testpass123',
        )

        response = self.client.get(
            reverse(
                'reviews:edit',
                kwargs={'pk': self.review.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_edit.html')
        self.assertIn('form', response.context)
        self.assertIn('review', response.context)

    def test_owner_can_edit_review(self):
        """Владелец может изменить свой отзыв."""
        self.client.login(
            username='olga',
            password='testpass123',
        )

        response = self.client.post(
            reverse(
                'reviews:edit',
                kwargs={'pk': self.review.pk},
            ),
            data={
                'rating': 4,
                'comments': 'Изменённый отзыв',
            },
        )

        self.assertRedirects(
            response,
            reverse(
                'products:detail',
                kwargs={'slug': self.product.slug},
            ),
        )

        self.review.refresh_from_db()

        self.assertEqual(self.review.rating, 4)
        self.assertEqual(
            self.review.comments,
            'Изменённый отзыв',
        )

    def test_other_user_cannot_edit_review(self):
        """Другой пользователь не может редактировать чужой отзыв."""
        self.client.login(
            username='petr',
            password='testpass123',
        )

        response = self.client.get(
            reverse(
                'reviews:edit',
                kwargs={'pk': self.review.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_owner_can_open_delete_page(self):
        """Владелец может открыть страницу удаления."""
        self.client.login(
            username='olga',
            password='testpass123',
        )

        response = self.client.get(
            reverse(
                'reviews:delete',
                kwargs={'pk': self.review.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_delete.html')
        self.assertIn('review', response.context)

    def test_owner_can_delete_review(self):
        """Владелец может удалить свой отзыв."""
        self.client.login(
            username='olga',
            password='testpass123',
        )

        response = self.client.post(
            reverse(
                'reviews:delete',
                kwargs={'pk': self.review.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse(
                'products:detail',
                kwargs={'slug': self.product.slug},
            ),
        )

        self.assertFalse(
            Review.objects.filter(pk=self.review.pk).exists()
        )

    def test_other_user_cannot_delete_review(self):
        """Другой пользователь не может удалить чужой отзыв."""
        self.client.login(
            username='petr',
            password='testpass123',
        )

        response = self.client.post(
            reverse(
                'reviews:delete',
                kwargs={'pk': self.review.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Review.objects.filter(pk=self.review.pk).exists()
        )


