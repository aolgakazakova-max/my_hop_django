from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.settings.development import DEBUG
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .api_urls import router
from users.api_views import RegisterApiView
from orders.api_views import CartAPIView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    path('users/', include('users.urls')),
]


api_patterns = [
    path('', include(router.urls)),

    path(
        'users/register/',
        RegisterApiView.as_view(),
        name='register',
    ),

    path(
        'users/login/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),

    path(
        'users/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh',
    ),

    path(
        'schema/',
        SpectacularAPIView.as_view(),
        name='schema',
    ),

    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'cart/',
        CartAPIView.as_view(),
        name='cart-api',
),
]


urlpatterns += [
    path('api/', include(api_patterns)),
]


if DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )