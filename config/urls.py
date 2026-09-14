from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from config.settings.development import DEBUG


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    path('users/', include('users.urls')),
]


if DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

