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
    address_title = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=1000)

    def __str__(Self):
        return Self.address_title

    
class Company(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class MedCategory(models.Model):
    # surgical ins / medicine / something else
    category_name = models.CharField(max_length=1000)
    cat_image=models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return self.category_name

class MedFormula(models.Model):
    category = models.ForeignKey(MedCategory, on_delete=models.CASCADE, related_name='generic_name', null=True)
    formula_name = models.CharField(max_length=1000)

    def __str__(self):
        return self.formula_name
    
class MedImage(models.Model):
    item = models.OneToOneField('Item', on_delete=models.CASCADE, related_name='image', null=True)  # One-to-One relationship
    image = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return f"Image for {self.item.name}"

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
    price = models.FloatField(null=True, blank=True)
    # packaging_unit = ml/box/strip 
    packaging_unit = models.CharField(max_length=20, null=True)
    min_threshold_qty = models.IntegerField()
    max_threshold_qty = models.IntegerField()
    current_qty = models.IntegerField(default=0)
    # qty=0 : finished / 0 < qty < min threshold : insufficient / min threshold < qty < max threshold : sufficient / max threshold < qty : surplus
    qty_status = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    usage = models.CharField(max_length=1000, blank=True, null=True)
    precautions = models.CharField(max_length=1000, blank=True, null=True)
    qty_sold = models.IntegerField(default=0)
    # item_status: active / inactive 
    item_status = models.CharField(max_length=20, default='active')
    is_ordered = models.CharField(max_length=10, default=False)

    def __str__(self):
        return f"Item #{self.id}"
    

#following table will hold record of orders made by warehouse to the vendors
class InventoryOrders(models.Model):
    orderDate = models.DateTimeField(auto_now_add=True)
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='itemid')
    # qty_ordered = models.IntegerField()
    qty_ordered = models.CharField(max_length=50)
    qty_received = models.CharField(max_length=50, default=0)
    # order_status: pending / completed / returned
    order_status = models.CharField(max_length=50)
    vendorID = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendorId') 

    def __str__(self):
        return f"Order #{self.id}"


class Symptom(models.Model):
    med_formula = models.ForeignKey(MedFormula, on_delete=models.CASCADE, related_name='med_formula')
    symptom = models.CharField(max_length=200, null=True)

class QRCode(models.Model):
    image = models.ImageField(upload_to='qr_codes/')

    def save(self, *args, **kwargs):
        if QRCode.objects.exists() and not self.pk:
            # Delete the existing QR code
            QRCode.objects.all().delete()
        super().save(*args, **kwargs)

    def _str_(self):
        return f"QR Code {self.pk}"