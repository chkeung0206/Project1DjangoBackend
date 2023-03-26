from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.authtoken.views import Token
from django.contrib.auth.models import User
from .models import Category, Product, Offer, CartItem, Cart, OrderItem, Order

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user = user)
        return user

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_inventory = serializers.IntegerField(source='product.inventory', read_only=True)
    subtotal = serializers.ReadOnlyField()
    class Meta:
        model = CartItem
        fields = '__all__'
        extra_kwargs = {
            'offer': {
                'allow_empty': True
            }
        }

class CartSerializer(ModelSerializer):
    total = serializers.ReadOnlyField()
    class Meta:
        model = Cart
        fields = '__all__'

class OfferSerializer(ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

class OrderItemSerializer(ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs = {
            'offer': {
                'allow_empty': True
            }
        }

class OrderSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        fields = '__all__'