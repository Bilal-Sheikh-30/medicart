from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    user_type_choices = [
        ('user', 'user'),
        ('sales', 'sales emp'),
        ('warehouse', 'warehouse emp'),
        ('rider', 'rider'),
    ]
    user_type = models.CharField(max_length=12, choices=user_type_choices)
    gender = models.CharField(max_length=10)
    

class Address(models.Model):
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='userid')
    address_title = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)

    def __str__(Self):
        return Self.address_title

class MedFormula(models.Model):
    formula_name = models.CharField(max_length=1000)

    def __str__(self):
        return self.formula_name
    
class Company(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class MedCategory(models.Model):
    # surgical ins / medicine / something else
    category_name = models.CharField(max_length=1000)

    def __str__(self):
        return self.category_name
    
class Item(models.Model):
    name = models.CharField(max_length=100)
    med_formula = models.ForeignKey(MedFormula, on_delete=models.CASCADE, related_name='medFormula', blank=True, null=True)
    category = models.ForeignKey(MedCategory, on_delete=models.CASCADE, related_name='category')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='itemBy', null=True)
    # mg of medicine
    dosage_strength = models.CharField(max_length=50, null=True)
    # form : tablet / syrup / capsules
    form = models.CharField(max_length=50, null=True, blank=True)
    # ml of syp / tabs per strip
    qty_per_pack = models.IntegerField(null=True, blank=True)
    price_per_strip = models.FloatField(null=True, blank=True)
    min_threshold_qty = models.IntegerField()
    max_threshold_qty = models.IntegerField()
    qty_status = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    usage = models.CharField(max_length=1000, blank=True, null=True)
    precautions = models.CharField(max_length=1000, blank=True, null=True)
    qty_sold = models.IntegerField()

    def __str__(self):
        return self.name
    

#following table will hold record of orders made by warehouse to the vendors
class InventoryOrders(models.Model):
    orderDate = models.DateTimeField(auto_now_add=True)
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='itemid')
    qty_ordered = models.IntegerField()
    order_status = models.CharField(max_length=50)
    vendorID = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendorId') 

    def __str__(self):
        return self.id

class MedImage(models.Model):
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='itemId')
    image = models.ImageField(upload_to='photos/', blank=True, null=True)

class Symptom(models.Model):
    med_formula = models.ForeignKey(MedFormula, on_delete=models.CASCADE, related_name='med_formula')
    symptom = models.CharField(max_length=200, null=True)
