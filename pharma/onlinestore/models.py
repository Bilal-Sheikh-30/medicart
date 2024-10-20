from django.db import models
from inventory.models import CustomUser, Item, Address
# Create your models here.

class Cart(models.Model):
    userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart')
    prodId = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='prodid')
    prodPrice = models.FloatField()
    qty = models.IntegerField()

    def __str__(self):
        return self.id
    
class Order(models.Model):
    placed_on = models.DateTimeField(auto_now_add=True)
    cartId = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartid')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='addressid')
    net_total = models.IntegerField()
    rider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rider', blank=True, null=True)
    payment_mode = models.CharField(max_length=20)
    payment_receipt = models.ImageField(upload_to='payments/', blank=True, null=True)
    payment_status = models.CharField(max_length=50)

    def __str__(self):
        return self.id
    