from rest_framework import serializers
from yet_another_pixel_draw import models
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.core.cache import cache
from PIL import Image
import numpy as np
from math import ceil

SMALLEST_SQUARE_SIZE = 128
MAX_GRID_SIZE = 10


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
        pil_img = self.validated_data['file'].file
        pil_img = Image.open(pil_img)
        pil_img = pil_img.convert(mode="RGB")
        img = np.array(pil_img)
        for grid_count in range(MAX_GRID_SIZE):
            field = self._get_grid(img)
            cache.set(f'level{grid_count}', field, None)
            pil_img = pil_img.resize(size=(ceil(img.shape[0]/2), ceil(img.shape[1]/2)))
            img = np.array(pil_img)

    def _get_grid(self, img):
        field = np.ndarray(
            shape=(
                ceil(img.shape[0] / SMALLEST_SQUARE_SIZE),
                ceil(img.shape[1] / SMALLEST_SQUARE_SIZE)
            ),
            dtype=np.object
        )
        for i in range(field.shape[0]):
            for j in range(field.shape[0]):
                field[i, j] = img[i * SMALLEST_SQUARE_SIZE: (i + 1) * SMALLEST_SQUARE_SIZE,
                              j * SMALLEST_SQUARE_SIZE: (j + 1) * SMALLEST_SQUARE_SIZE]
        return field


class GetGridSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    size = serializers.IntegerField()

    def get_proper_field(self):
        x = self.validated_data['x']
        y = self.validated_data['y']
        size = self.validated_data['size']
        grid = cache.get(f'level{size}')
        return grid[x, y]

# {"x": 1, "y": 1, "color": "#111111"}
