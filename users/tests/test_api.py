from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterApiTests(APITestCase):
    """Тесты API регистрации."""

    def test_api_register_creates_user(self):
        """API создаёт нового пользователя."""
        response = self.client.post(
            reverse('register'),
            data={
                'email': 'api@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                email='api@example.com'
            ).exists()
        )

    def test_api_register_returns_email(self):
        """API возвращает email пользователя."""
        response = self.client.post(
            reverse('register'),
            data={
                'email': 'api@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data['email'],
            'api@example.com',
        )

    def test_api_password_is_not_returned(self):
        """Пароль не должен возвращаться API."""
        response = self.client.post(
            reverse('register'),
            data={
                'email': 'api@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertNotIn(
            'password',
            response.data,
        )

    def test_api_duplicate_email_is_rejected(self):
        """Повторная регистрация с email отклоняется."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='StrongPass123!',
        )

        response = self.client.post(
            reverse('register'),
            data={
                'email': 'existing@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_api_email_is_saved_in_lowercase(self):
        """Email через API сохраняется в нижнем регистре."""
        response = self.client.post(
            reverse('register'),
            data={
                'email': 'API@EXAMPLE.COM',
                'password': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                email='api@example.com'
            ).exists()
        )





