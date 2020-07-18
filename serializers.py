from json import loads
from math import ceil, floor

import numpy as np
from PIL import Image
from django.core.cache import cache
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from yet_another_pixel_draw import models

SMALLEST_SQUARE_SIZE = 128
MAX_GRID_SIZE = 10


class CurrentFieldSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.date = None

    def save(self, user):
        x = self.validated_data['x']
        y = self.validated_data['y']
        color = self.validated_data['color']
        pixel = models.PixelHistory.objects.create(x=x, y=y, color=color, user=user)
        self.date = pixel.date
        self.validated_data['date'] = self.date
        color = np.array(loads(color))

        x_grid, x_in_grid = divmod(x, SMALLEST_SQUARE_SIZE)
        y_grid, y_in_grid = divmod(y, SMALLEST_SQUARE_SIZE)
        cur_grid = cache.get(f'level0_{x_grid}_{y_grid}')
        color_orig = cur_grid[x_in_grid, y_in_grid]

        for grid_num in range(MAX_GRID_SIZE):
            x_grid, x_in_grid = divmod(x, SMALLEST_SQUARE_SIZE * 2 ** grid_num)
            y_grid, y_in_grid = divmod(y, SMALLEST_SQUARE_SIZE * 2 ** grid_num)
            cur_grid = cache.get(f'level{grid_num}_{x_grid}_{y_grid}')
            x_in_grid = floor(x_in_grid / (2 ** grid_num))
            y_in_grid = floor(y_in_grid / (2 ** grid_num))
            cur_grid[x_in_grid, y_in_grid] += ((color - color_orig) / (4 ** grid_num)).astype(np.uint8)
            cache.set(f'level{grid_num}_{x_grid}_{y_grid}', cur_grid, None)

    class Meta:
        model = models.PixelHistory
        fields = ['x', 'y', 'color']


class PixelHistorySerializer(serializers.Serializer):
    date = serializers.DateTimeField()

    def get(self):
        if self.is_valid():
            date = self.validated_data['date']
            history_data = models.PixelHistory.objects.all().filter(date__gt=date).order_by('date')
            history_serializer = HistoryElementSerializer(history_data, many=True)
            res = JSONRenderer().render(history_serializer.data)
            return res

class HistoryElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PixelHistory
        fields = ['x', 'y', 'color', 'date']

class NewFieldSerializer(serializers.Serializer):
    file = serializers.ImageField()

    def save(self, user, **kwargs):
        pil_img = self.validated_data['file'].file
        pil_img = Image.open(pil_img)
        pil_img = pil_img.convert(mode="RGB")
        img = np.array(pil_img)
        for grid_count in range(MAX_GRID_SIZE):
            field = self._get_grid(img)
            for i in range(0, field.shape[0]):
                for j in range(0, field.shape[1]):
                    cache.set(f'level{grid_count}_{i}_{j}', field[i, j], None)
            cache.set(f'grid_size_{grid_count}', field.shape, None)
            pil_img = pil_img.resize(size=(ceil(img.shape[1] / 2), ceil(img.shape[0] / 2)), resample=Image.BOX)
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
            for j in range(field.shape[1]):
                field[i, j] = img[i * SMALLEST_SQUARE_SIZE: (i + 1) * SMALLEST_SQUARE_SIZE,
                              j * SMALLEST_SQUARE_SIZE: (j + 1) * SMALLEST_SQUARE_SIZE]
        return field


class GetGridSerializer(serializers.ModelSerializer):
    def get_proper_field(self):
        x = self.validated_data['x']
        y = self.validated_data['y']
        size = self.validated_data['size']
        grid = cache.get(f'level{size}_{x}_{y}')
        return grid

    class Meta:
        model = models.CurrentField
        fields = ["x", "y", "size"]


class GridSize(serializers.Serializer):
    size = serializers.IntegerField()
# {"x": 1, "y": 1, "color": "#111111"}
