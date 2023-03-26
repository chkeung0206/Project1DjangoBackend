from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Category(models.Model):

    name = models.CharField(max_length = 30)

    def __str__(self):
        return self.name

class Product(models.Model):

    name = models.CharField(max_length = 100)
    image = models.ImageField(upload_to='product_image/', height_field=None, width_field=None)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=19, decimal_places=4)
    inventory = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(9999)])
    description = models.CharField(max_length = 500)
    hot = models.BooleanField() 

    def __str__(self):
        return self.name

class Offer(models.Model):

    name = models.CharField(max_length = 100)
    offer_type = models.IntegerField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    active_from = models.DateTimeField()
    active_until = models.DateTimeField()

class Cart(models.Model):

    session = models.CharField(max_length = 128)
    last_updated = models.DateField(auto_now=True)

    @property
    def total(self):
        return sum(obj.subtotal for obj in self.cartitem_set.all())

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(9999)])
    offer = models.ManyToManyField(Offer)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    time_placed = models.DateTimeField(auto_now_add=True)
    delivery_fee = models.DecimalField(max_digits=19, decimal_places=4)
    total = models.DecimalField(max_digits=19, decimal_places=4)
    remarks = models.CharField(max_length = 200)
    active = models.BooleanField(default=True)      

class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(9999)])
    offer = models.ManyToManyField(Offer)
    subtotal = models.DecimalField(max_digits=19, decimal_places=4)
        