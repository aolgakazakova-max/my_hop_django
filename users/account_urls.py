
from django.urls import path

from .views import profile_view

app_name = 'account'

urlpatterns = [
    path(
        '',
        profile_view,
        name='home',
    ),
]


