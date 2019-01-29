from django.db import models
from django.db.models import Manager


class H(models.Model):
    v = models.IntegerField(default=0)

    def refresh_from_db(self, *args, **kwargs):
        return super().refresh_from_db(*args, **kwargs)


class M(models.Model):
    v = models.IntegerField(default=0)
    h = models.ForeignKey(H, on_delete=models.CASCADE)


class L(models.Model):
    v = models.IntegerField(default=0)
    m = models.ForeignKey(M, on_delete=models.CASCADE)


class T(models.Model):
    v = models.IntegerField(default=0)
    start = models.DateTimeField()
    end = models.DateTimeField()
    storage = models.TextField(null=True)


class S(models.Model):  # store
    v = models.IntegerField(default=0)


class A(models.Model):  # author
    v = models.IntegerField(default=0)


class B(models.Model):  # book
    a = models.ManyToManyField(A)
    s = models.ManyToManyField(S)
    v = models.IntegerField(default=0)


class Im(models.Model):
    i = models.ImageField(width_field='w')
    w = models.IntegerField()