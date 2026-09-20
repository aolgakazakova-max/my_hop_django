from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','slug','parent']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    avg_rating = serializers.FloatField(read_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'price',
            'category',
            'image',
            'stock',
            'is_active',
            'avg_rating'
        ]

