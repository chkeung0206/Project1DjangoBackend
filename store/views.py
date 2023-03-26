from .serializers import UserSerializer, CategorySerializer, ProductSerializer, OfferSerializer, CartItemSerializer, CartSerializer, OrderItemSerializer, OrderSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Category, Product, Offer, CartItem, Cart, OrderItem, Order
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from math import ceil
from datetime import date, timedelta

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        conditions = {}
        required_category = self.request.headers.get('required-category')
        if required_category:
            conditions['category'] = required_category
        search_keyword = self.request.headers.get('search-keyword')
        if search_keyword:
            conditions['name__contains'] = search_keyword
        return Product.objects.filter(**conditions)

    def list(self, request):
        results_per_page = int(request.headers.get('results-per-page'))
        start_pt = results_per_page * (int(request.headers.get('page-no')) - 1)
        data = self.serializer_class(self.get_queryset()[start_pt : start_pt + results_per_page], many=True).data
        no_of_pages = ceil(self.get_queryset().count() / results_per_page)
        return Response({
            'data' : data,
            'no-of-pages' : no_of_pages,
        })
    
class HotProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(hot=True)

class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer

    def get_cart(self):
        session = self.request.headers.get('session')
        return Cart.objects.filter(session=session, 
                                   last_updated__gte=date.today()-timedelta(days=30)).first()

    def get_queryset(self):
        cart = self.get_cart()
        return cart.cartitem_set.all() if cart else None  
    
    def retrieve(self, request, pk=None):
        cart_item = CartItem.objects.get(id=pk)
        data = self.serializer_class(cart_item).data
        cart = self.get_cart()
        response = {'data' : data}
        if cart:
            response.update({
                'cart-total' : cart.total,
                'cart-expiration-time' : cart.last_updated + timedelta(days=30),
            })
        return Response(response)
    
    def list(self, request):
        data = self.serializer_class(self.get_queryset(), many=True).data
        cart = self.get_cart()
        response = {'data' : data}
        if cart:
            response.update({
                'cart-total' : cart.total,
                'cart-expiration-time' : cart.last_updated + timedelta(days=30),
            })
        return Response(response)
    
    def create(self, request, *args, **kwargs):
        cart = self.get_cart()
        if not cart:
            cart_serializer = CartSerializer(data={
                'session' : request.headers.get('session'),
            })
            if cart_serializer.is_valid():
                cart = cart_serializer.save()
        request.data['cart'] = cart.id
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()           
        return Response(serializer.data['id'])
    
    def update(self, request, pk=None):
        session = request.headers.get('session')
        cart_item = CartItem.objects.get(id=pk)
        if cart_item and cart_item.cart.session == session:
            serializer = self.serializer_class(cart_item, data=request.data)      
            if serializer.is_valid():
                serializer.save()  
                return Response(serializer.data['id'])
        return Response({}, status=404)
    
    def destroy(self, request, pk=None):
        session = request.headers.get('session')
        cart_item = CartItem.objects.get(id=pk)
        if cart_item and cart_item.cart.session == session:
            cart = cart_item.cart        
            cart_item.delete()
            if not cart.cartitem_set.exists():
                cart.delete()
                response = {
                    'cart-total' : 0,
                    'cart-expiration-time' : date.today(),
                }
                return Response(response)
            response = {
                'cart-total' : cart.total,
                'cart-expiration-time' : cart.last_updated + timedelta(days=30),
            }
            return Response(response)
        return Response({}, status=404)
        
class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        order = Order.objects.filter(user=self.request.user, active=True).first()
        return order.orderitem_set.all() if order else None
    
class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, active=True)
    
    def create(self, request, *args, **kwargs):
        session = request.headers.get('session')
        cart = Cart.objects.filter(session=session).first()
        serializer = self.serializer_class(data={
            'delivery_fee' : 1234,
            'total' : cart.total,
            'remarks' : '...'
        }, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()        
        cart_items = cart.cartitem_set.all() if cart else None
        for cart_item in cart_items:
            order_item = OrderItem(
                order = order,    
                product = cart_item.product,
                quantity = cart_item.quantity,
                subtotal = cart_item.subtotal
            )
            order_item.save()
            order_item.product.inventory -= order_item.quantity
            order_item.product.save()
            cart_item.delete()
        cart.delete()
        return Response(serializer.data['id'])

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
        })
