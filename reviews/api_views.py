from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated

from orders.models import OrderItem

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related(
        'product',
        'user',
    ).all()

    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data['product']

        has_purchased = OrderItem.objects.filter(
            order__user=user,
            order__status__in=[
                'paid',
                'shipped',
                'delivered',
            ],
            product=product,
        ).exists()

        if not has_purchased:
            raise PermissionDenied(
                'Вы можете оставить отзыв только на купленный товар.'
            )

        serializer.save(user=user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied(
                'You can edit only your own review.'
            )

        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied(
                'You can delete only your own review.'
            )

        instance.delete()

