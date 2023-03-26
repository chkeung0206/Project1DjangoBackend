from django.urls import path, include
from .views import UserViewSet, CategoryViewSet, ProductViewSet, HotProductViewSet, OfferViewSet, CartItemViewSet, OrderItemViewSet, OrderViewSet
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('user', UserViewSet, basename = 'user')
router.register('category', CategoryViewSet, basename = 'category')
router.register('product', ProductViewSet, basename = 'product')
router.register('hot_product', HotProductViewSet, basename = 'hot_product')
router.register('offer', OfferViewSet, basename = 'offer')
router.register('cart_item', CartItemViewSet, basename = 'cart_item')
router.register('order_item', OrderItemViewSet, basename = 'order_item')
router.register('order', OrderViewSet, basename = 'order')

urlpatterns = [
    path('', include(router.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)