# Generated by Django 5.1.2 on 2024-10-22 08:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_medformula_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medimage',
            name='itemId',
        ),
        migrations.AddField(
            model_name='medimage',
            name='item',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image', to='inventory.item'),
        ),
    ]
