from django.contrib import admin
from .models import Category, Product, CartItem, Cart, Offer, OrderItem, Order

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Offer)
admin.site.register(OrderItem)
admin.site.register(Order)