# Generated by Django 2.1.5 on 2019-01-09 07:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_auto_20190109_0713'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='place',
            options={'ordering': ['id']},
        ),
    ]
