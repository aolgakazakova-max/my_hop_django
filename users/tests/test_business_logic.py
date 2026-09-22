from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order

from ..forms import (
    ProfileForm,
    RegisterForm,
    UserPasswordChangeForm,
)
from ..models import Profile

User = get_user_model()


class ProfileModelTests(TestCase):
    """Тесты модели Profile."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

    def test_profile_creation(self):
        """Проверяем создание профиля."""
        profile = Profile.objects.create(
            user=self.user,
            full_name='Olga Kazakova',
            phone='+123456789',
            city='Amsterdam',
            address='Main Street 10',
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.full_name, 'Olga Kazakova')
        self.assertEqual(profile.phone, '+123456789')
        self.assertEqual(profile.city, 'Amsterdam')
        self.assertEqual(profile.address, 'Main Street 10')

    def test_profile_str(self):
        """Проверяем строковое представление профиля."""
        profile = Profile.objects.create(
            user=self.user,
        )

        self.assertEqual(
            str(profile),
            'Profile of olga',
        )

    def test_profile_one_to_one_relation(self):
        """Проверяем связь OneToOne."""
        Profile.objects.create(
            user=self.user,
        )

        with self.assertRaises(Exception):
            Profile.objects.create(
                user=self.user,
            )


class RegisterFormTests(TestCase):
    """Тесты формы регистрации."""

    def valid_data(self):
        return {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }

    def test_valid_form(self):
        """Корректные данные проходят валидацию."""
        form = RegisterForm(
            data=self.valid_data()
        )

        self.assertTrue(form.is_valid())

    def test_existing_username_is_invalid(self):
        """Существующий username запрещён."""
        User.objects.create_user(
            username='newuser',
            email='old@example.com',
            password='StrongPass123!',
        )

        form = RegisterForm(
            data=self.valid_data()
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'username',
            form.errors,
        )

    def test_existing_email_is_invalid(self):
        """Существующий email запрещён."""
        User.objects.create_user(
            username='olduser',
            email='newuser@example.com',
            password='StrongPass123!',
        )

        form = RegisterForm(
            data=self.valid_data()
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'email',
            form.errors,
        )

    def test_password_confirmation_is_invalid(self):
        """Пароли должны совпадать."""
        data = self.valid_data()
        data['password_confirm'] = 'DifferentPass123!'

        form = RegisterForm(
            data=data
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            '__all__',
            form.errors,
        )

    def test_save_creates_user(self):
        """save() создаёт пользователя."""
        form = RegisterForm(
            data=self.valid_data()
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(
            user.username,
            'newuser',
        )
        self.assertEqual(
            user.email,
            'newuser@example.com',
        )
        self.assertTrue(
            user.check_password(
                'StrongPass123!'
            )
        )

    def test_profile_form_is_valid(self):
        """ProfileForm принимает корректные данные."""
        form = ProfileForm(
            data={
                'full_name': 'Olga Kazakova',
                'phone': '+123456789',
                'city': 'Amsterdam',
                'address': 'Main Street 10',
            }
        )

        self.assertTrue(form.is_valid())


class RegisterViewTests(TestCase):
    """Тесты страницы регистрации."""

    def valid_data(self):
        return {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }

    def test_register_page_is_available(self):
        """Страница регистрации доступна."""
        response = self.client.get(
            reverse('users:register')
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            'register.html',
        )

    def test_user_can_register(self):
        """Пользователь может зарегистрироваться."""
        response = self.client.post(
            reverse('users:register'),
            data=self.valid_data(),
        )

        self.assertRedirects(
            response,
            reverse('products:list'),
        )

        self.assertTrue(
            User.objects.filter(
                username='newuser'
            ).exists()
        )

    def test_user_is_logged_in_after_registration(self):
        """После регистрации пользователь автоматически входит."""
        self.client.post(
            reverse('users:register'),
            data=self.valid_data(),
        )

        user = User.objects.get(
            username='newuser'
        )

        self.assertEqual(
            int(
                self.client.session['_auth_user_id']
            ),
            user.pk,
        )

    def test_authenticated_user_is_redirected_from_register(self):
        """Авторизованный пользователь перенаправляется с регистрации."""
        user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse('users:register')
        )

        self.assertRedirects(
            response,
            reverse('products:list'),
        )


class LoginViewTests(TestCase):
    """Тесты входа пользователя."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

    def test_login_page_is_available(self):
        """Страница входа доступна."""
        response = self.client.get(
            reverse('users:login')
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            'login.html',
        )

    def test_user_can_login_with_email(self):
        """Пользователь может войти по email."""
        response = self.client.post(
            reverse('users:login'),
            data={
                'email': 'olga@example.com',
                'password': 'StrongPass123!',
            },
        )

        self.assertRedirects(
            response,
            reverse('products:list'),
        )

        self.assertEqual(
            int(
                self.client.session['_auth_user_id']
            ),
            self.user.pk,
        )

    def test_email_is_case_insensitive(self):
        """Email не зависит от регистра."""
        response = self.client.post(
            reverse('users:login'),
            data={
                'email': 'OLGA@EXAMPLE.COM',
                'password': 'StrongPass123!',
            },
        )

        self.assertRedirects(
            response,
            reverse('products:list'),
        )

    def test_invalid_password_does_not_login(self):
        """Неверный пароль не выполняет вход."""
        response = self.client.post(
            reverse('users:login'),
            data={
                'email': 'olga@example.com',
                'password': 'WrongPassword!',
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotIn(
            '_auth_user_id',
            self.client.session,
        )

    def test_unknown_email_does_not_login(self):
        """Несуществующий email не выполняет вход."""
        response = self.client.post(
            reverse('users:login'),
            data={
                'email': 'unknown@example.com',
                'password': 'StrongPass123!',
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotIn(
            '_auth_user_id',
            self.client.session,
        )

    def test_authenticated_user_is_redirected_from_login(self):
        """Авторизованный пользователь перенаправляется с login."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:login')
        )

        self.assertRedirects(
            response,
            reverse('products:list'),
        )


class LogoutViewTests(TestCase):
    """Тесты выхода пользователя."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

    def test_logout_logs_user_out(self):
        """Проверяем выход из аккаунта."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:logout')
        )

        self.assertRedirects(
            response,
            reverse('products:list'),
        )

        self.assertNotIn(
            '_auth_user_id',
            self.client.session,
        )


class ProfileViewTests(TestCase):
    """Тесты страницы профиля."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

        self.profile = Profile.objects.create(
            user=self.user,
            full_name='Olga Kazakova',
            phone='+123456789',
            city='Amsterdam',
            address='Main Street 10',
        )

    def test_authenticated_user_can_open_profile(self):
        """Авторизованный пользователь видит профиль."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:profile')
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            'profile.html',
        )

        self.assertEqual(
            response.context['profile'],
            self.profile,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        """Неавторизованный пользователь отправляется на login."""
        response = self.client.get(
            reverse('users:profile')
        )

        self.assertRedirects(
            response,
            reverse('users:login'),
        )

    def test_profile_belongs_to_current_user(self):
        """Показывается профиль текущего пользователя."""
        another_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='StrongPass123!',
        )

        another_profile = Profile.objects.create(
            user=another_user,
            full_name='Other User',
        )

        self.client.force_login(another_user)

        response = self.client.get(
            reverse('users:profile')
        )

        self.assertEqual(
            response.context['profile'],
            another_profile,
        )


class ProfileEditViewTests(TestCase):
    """Тесты редактирования профиля."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

        self.profile = Profile.objects.create(
            user=self.user,
            full_name='Olga Kazakova',
            phone='+123456789',
            city='Amsterdam',
            address='Main Street 10',
        )

    def test_authenticated_user_can_open_profile_edit(self):
        """Авторизованный пользователь может открыть редактирование."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:profile_edit')
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            'profile_edit.html',
        )

    def test_profile_can_be_updated(self):
        """Пользователь может изменить данные профиля."""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('users:profile_edit'),
            data={
                'full_name': 'Olga New Name',
                'phone': '+987654321',
                'city': 'Rotterdam',
                'address': 'New Street 25',
            },
        )

        self.assertRedirects(
            response,
            reverse('users:profile'),
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.full_name,
            'Olga New Name',
        )
        self.assertEqual(
            self.profile.phone,
            '+987654321',
        )
        self.assertEqual(
            self.profile.city,
            'Rotterdam',
        )
        self.assertEqual(
            self.profile.address,
            'New Street 25',
        )

    def test_anonymous_user_cannot_edit_profile(self):
        """Неавторизованный пользователь не может редактировать профиль."""
        response = self.client.get(
            reverse('users:profile_edit')
        )

        self.assertRedirects(
            response,
            f'{reverse("users:login")}'
            f'?next={reverse("users:profile_edit")}',
        )

    def test_profile_is_created_if_missing(self):
        """Если профиля нет, он создаётся автоматически."""
        self.profile.delete()

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:profile_edit')
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            Profile.objects.filter(
                user=self.user
            ).exists()
        )


class PasswordChangeViewTests(TestCase):
    """Тесты смены пароля."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

    def test_password_change_form_is_valid(self):
        """Форма смены пароля принимает правильные данные."""
        form = UserPasswordChangeForm(
            user=self.user,
            data={
                'old_password': 'StrongPass123!',
                'new_password1': 'NewStrongPass456!',
                'new_password2': 'NewStrongPass456!',
            },
        )

        self.assertTrue(
            form.is_valid()
        )

    def test_password_change_page_is_available(self):
        """Страница смены пароля доступна."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:password_change')
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            'password_change.html',
        )

    def test_password_can_be_changed(self):
        """Пользователь может изменить пароль."""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('users:password_change'),
            data={
                'old_password': 'StrongPass123!',
                'new_password1': 'NewStrongPass456!',
                'new_password2': 'NewStrongPass456!',
            },
        )

        self.assertRedirects(
            response,
            reverse('users:profile'),
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                'NewStrongPass456!'
            )
        )

    def test_wrong_old_password_is_rejected(self):
        """Неверный текущий пароль отклоняется."""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('users:password_change'),
            data={
                'old_password': 'WrongPassword!',
                'new_password1': 'NewStrongPass456!',
                'new_password2': 'NewStrongPass456!',
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                'StrongPass123!'
            )
        )

    def test_anonymous_user_cannot_change_password(self):
        """Неавторизованный пользователь не может менять пароль."""
        response = self.client.get(
            reverse('users:password_change')
        )

        self.assertRedirects(
            response,
            f'{reverse("users:login")}'
            f'?next={reverse("users:password_change")}',
        )


class OrderHistoryViewTests(TestCase):
    """Тесты истории заказов."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='olga',
            email='olga@example.com',
            password='StrongPass123!',
        )

        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='StrongPass123!',
        )

    def create_order(
        self,
        user,
        status=Order.Status.PENDING,
        total_price='100.00',
    ):
        return Order.objects.create(
            user=user,
            status=status,
            total_price=total_price,
            shipping_address='Amsterdam, Main Street 10',
        )

    def test_order_history_page_is_available(self):
        """Страница истории заказов доступна."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:orders')
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            'order_history.html',
        )

    def test_order_history_contains_only_current_user_orders(self):
        """Показываются только заказы текущего пользователя."""
        own_order = self.create_order(
            self.user,
            total_price='150.00',
        )

        other_order = self.create_order(
            self.other_user,
            total_price='250.00',
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:orders')
        )

        orders = list(
            response.context['orders']
        )

        self.assertIn(
            own_order,
            orders,
        )

        self.assertNotIn(
            other_order,
            orders,
        )

    def test_order_history_can_filter_by_status(self):
        """Историю можно фильтровать по статусу."""
        pending_order = self.create_order(
            self.user,
            status=Order.Status.PENDING,
        )

        paid_order = self.create_order(
            self.user,
            status=Order.Status.PAID,
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:orders'),
            data={
                'status': Order.Status.PAID,
            },
        )

        orders = list(
            response.context['orders']
        )

        self.assertIn(
            paid_order,
            orders,
        )

        self.assertNotIn(
            pending_order,
            orders,
        )

        self.assertEqual(
            response.context['selected_status'],
            Order.Status.PAID,
        )

    def test_order_history_without_orders(self):
        """Для пользователя без заказов история пустая."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('users:orders')
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context['orders'].count(),
            0,
        )

    def test_anonymous_user_cannot_open_order_history(self):
        """Неавторизованный пользователь не может открыть историю."""
        response = self.client.get(
            reverse('users:orders')
        )

        self.assertRedirects(
            response,
            f'{reverse("users:login")}'
            f'?next={reverse("users:orders")}',
        )


