# Generated by Django 2.0.6 on 2018-06-27 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='main_category',
        ),
        migrations.RemoveField(
            model_name='product',
            name='minor_category',
        ),
        migrations.DeleteModel(
            name='MainCategory',
        ),
        migrations.DeleteModel(
            name='MinorCategory',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]