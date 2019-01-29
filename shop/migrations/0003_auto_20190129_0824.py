# Generated by Django 2.1.5 on 2019-01-29 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20190129_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='created',
            field=models.DateField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]