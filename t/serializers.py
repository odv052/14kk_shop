from rest_framework import serializers

from .models import H


class S(serializers.ModelSerializer):
    class Meta:
        model = H
        fields = ('v', )
