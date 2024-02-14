# Generated by Django 4.2.6 on 2024-02-14 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_payment_address_payment_city_payment_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address_line_1',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='country',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='first_name',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='last_name',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_note',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(max_length=500),
        ),
    ]
