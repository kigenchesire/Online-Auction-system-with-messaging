# Generated by Django 4.1.1 on 2022-11-15 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0020_biditems_actioneer_phonenumber_biditems_auctioneer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biditems',
            name='minimum_price',
            field=models.DecimalField(decimal_places=2, max_digits=50),
        ),
    ]
