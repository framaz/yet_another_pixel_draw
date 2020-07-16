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


class NewFieldSerializer(serializers.Serializer):
    file = serializers.ImageField()

    def save(self, user, **kwargs):
        img = self.validated_data['file'].file
        img = Image.open(img)
        img = np.array(img)
        field = np.ndarray(
            shape=(
                ceil(img.shape[0] / SMALLEST_SQUARE_SIZE),
                ceil(img.shape[1] / SMALLEST_SQUARE_SIZE)
                ),
            dtype=np.object
        )
        for i in range(field.shape[0]):
            for j in range(field.shape[0]):
                field[i, j] = img[i * SMALLEST_SQUARE_SIZE : (i + 1) * SMALLEST_SQUARE_SIZE,
                              j * SMALLEST_SQUARE_SIZE : (j + 1) * SMALLEST_SQUARE_SIZE]
        cache.set('level0', field, None)

class GetGridSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    size = serializers.IntegerField()

# {"x": 1, "y": 1, "color": "#111111"}
