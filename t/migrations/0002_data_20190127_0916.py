# Generated by Django 2.1.5 on 2019-01-27 09:16

from django.db import migrations
from django.db.migrations import RunPython


def add_hml_instances(app_config, schema_editor):
    H = app_config.get_model('t.H')
    M = app_config.get_model('t.M')
    L = app_config.get_model('t.L')
    # for h_i in range(2):
    #     h = H.objects.create(v=h_i)
    #     for m_i in range(2):
    #         m = M.objects.create(v=m_i, h=h)
    #         for l_i in range(3):
    #             L.objects.create(v=l_i, m=m)


class Migration(migrations.Migration):

    dependencies = [
        ('t', '0001_squashed_0009_auto_20190121_1206'),
    ]

    operations = [
        RunPython(add_hml_instances)
    ]