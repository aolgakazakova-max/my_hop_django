from rest_framework import serializers

from products.models import Product

from .models import Order, OrderItem
from .services import OutOfStock, create_order


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

    payment_type = serializers.ChoiceField(
        choices=Order.PaymentType.choices,
        default=Order.PaymentType.DEBIT,
        required=False,
    )

    items = OrderItemWriteSerializer(many=True)

    def validate_items(self, data):
        if not data:
            raise serializers.ValidationError(
                'Заказ должен содержать хотя бы один элемент.'
            )

        product_ids = [
            item['product_id']
            for item in data
        ]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                'Один и тот же товар нельзя добавить в заказ несколько раз.'
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user

        cart_items = []

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

            cart_items.append(
                {
                    'product': product,
                    'quantity': quantity,
                }
            )

        try:
            return create_order(
                user=user,
                cart=cart_items,
                data={
                    'shipping_address': validated_data['shipping_address'],
                    'payment_type': validated_data.get(
                        'payment_type',
                        Order.PaymentType.DEBIT,
                    ),
                },
            )
        except OutOfStock as error:
            raise serializers.ValidationError(
                {'items': str(error)}
            )
        except ValueError as error:
            raise serializers.ValidationError(
                {'detail': str(error)}
            )


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