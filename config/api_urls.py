from rest_framework.routers import DefaultRouter

from orders.api_views import OrderViewSet
from products.api_views import ProductViewSet, CategoryViewSet
from reviews.api_views import ReviewViewSet


router = DefaultRouter()

router.register(
    r'orders',
    OrderViewSet,
    basename='order',
)

router.register(
    r'products',
    ProductViewSet,
    basename='product',
)

router.register(
    r'categories',
    CategoryViewSet,
    basename='category',
)

router.register(
    r'reviews',
    ReviewViewSet,
    basename='review',
)