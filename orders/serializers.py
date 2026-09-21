from django.db import transaction
from rest_framework import serializers

from products.models import Product

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'quantity',
            'price',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'total_price',
            'shipping_address',
            'created_at',
            'items',
        ]


class OrderItemWriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    items = OrderItemWriteSerializer(many=True)

    def validate_items(self, data):
        if not data:
            raise serializers.ValidationError(
                'Заказ должен содержать хотя бы один элемент.'
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user

        with transaction.atomic():
            total = 0

            products = []

            for item in validated_data['items']:
                product_id = item['product_id']
                quantity = item['quantity']

                try:
                    product = Product.objects.get(
                        id=product_id,
                        is_active=True,
                    )
                except Product.DoesNotExist:
                    raise serializers.ValidationError(
                        f'Товар с id={product_id} не найден.'
                    )

                if product.stock < quantity:
                    raise serializers.ValidationError(
                        f'Не хватает "{product.name}" на складе.'
                    )

                total += product.price * quantity

                products.append(
                    {
                        'product': product,
                        'quantity': quantity,
                    }
                )

            order = Order.objects.create(
                user=user,
                status=Order.Status.PAID,
                total_price=total,
                shipping_address=validated_data['shipping_address'],
            )

            for item in products:
                product = item['product']
                quantity = item['quantity']

                product.stock -= quantity
                product.save(
                    update_fields=['stock'],
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

            return order


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(
        min_value=1,
        default=1,
    )


class CartUpdateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(
        min_value=1,
    )


class CartDeleteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()