from rest_framework import serializers
from yet_another_pixel_draw import models
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.core.cache import cache
from PIL import Image
import numpy as np
from math import ceil

SMALLEST_SQUARE_SIZE = 128

class CurrentFieldSerializer(serializers.ModelSerializer):
    def save(self, user):
        x = self.validated_data['x']
        y = self.validated_data['y']
        color = self.validated_data['color']
        models.PixelHistory.objects.create(x=x, y=y, color=color, user=user)

    class Meta:
        model = models.PixelHistory
        fields = ['x', 'y', 'color']


class GetGridSerialiser(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    size = serializers.IntegerField()

# {"x": 1, "y": 1, "color": "#111111"}
