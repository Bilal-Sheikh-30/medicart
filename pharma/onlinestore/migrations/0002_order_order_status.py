# Generated by Django 5.1.2 on 2024-11-01 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinestore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(max_length=20, null=True),
        ),
    ]