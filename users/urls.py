from django.urls import path

from .views import (
    login_view,
    logout_view,
    order_history_view,
    password_change_view,
    profile_edit_view,
    profile_view,
    register_view,
)

app_name = 'users'

urlpatterns = [
    path(
        'register/',
        register_view,
        name='register',
    ),
    path(
        'login/',
        login_view,
        name='login',
    ),
    path(
        'logout/',
        logout_view,
        name='logout',
    ),
    path(
        'profile/',
        profile_view,
        name='profile',
    ),
    path(
        'profile/edit/',
        profile_edit_view,
        name='profile_edit',
    ),
    path(
        'password/',
        password_change_view,
        name='password_change',
    ),
    path(
        'orders/',
        order_history_view,
        name='orders',
    ),
]


