# Generated by Django 2.1.5 on 2019-01-09 07:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_place_shop'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place2',
            fields=[
                ('place_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='polls.Place')),
            ],
            bases=('polls.place',),
        ),
    ]
