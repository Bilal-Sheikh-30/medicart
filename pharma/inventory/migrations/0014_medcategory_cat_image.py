# Generated by Django 5.1.2 on 2024-11-26 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_inventoryorders_qty_received'),
    ]

    operations = [
        migrations.AddField(
            model_name='medcategory',
            name='cat_image',
            field=models.ImageField(blank=True, null=True, upload_to='photos/'),
        ),
    ]
