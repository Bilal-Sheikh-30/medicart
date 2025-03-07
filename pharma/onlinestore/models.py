from django.db import models
from inventory.models import CustomUser, Item, Address
# Create your models here.
class Cart(models.Model):
    userID=models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_cart',null=True)
    placed_on = models.DateTimeField(auto_now_add=True,null=True)

class CartDetails(models.Model):
    cartId = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartinfo')
    prodId = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='prodid')
    prodPrice = models.CharField(max_length=20,null=True)
    qty = models.IntegerField()

    def __str__(self):
        return str(self.id)
    
class Order(models.Model):
    cartId = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartid')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='addressid')
    net_total = models.IntegerField()
    rider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rider', blank=True, null=True)
    payment_mode = models.CharField(max_length=20)
    # payment_receipt = models.ImageField(upload_to='payments/', blank=True, null=True)
    transaction_id = models.CharField(max_length=20,null=True ,default=None)
    payment_status = models.CharField(max_length=50)
    # pending / shipped / completed / canceled
    order_status = models.CharField(max_length=20, null=True)

    def __str__(self):
        return str(self.id)