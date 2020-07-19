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

        self.validated_data['last_color'] = color_orig

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

    def get(self, json=True):
        if self.is_valid():
            date = self.validated_data['date']
            history_data = models.PixelHistory.objects.all().filter(date__gt=date).order_by('date')
            if json:
                history_serializer = HistoryElementSerializer(history_data, many=True)
                res = JSONRenderer().render(history_serializer.data)
            else:
                res = history_data
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
        img = img.transpose(1, 0, 2)
        pil_img = Image.fromarray(img)

        models.CurrentField.objects.all().delete()
        img_split_and_cache(img)

def img_split_and_cache(img):

    pil_img = Image.fromarray(img)
    for grid_count in range(MAX_GRID_SIZE):
        field = get_grid(img)
        for i in range(0, field.shape[0]):
            for j in range(0, field.shape[1]):
                cache.set(f'level{grid_count}_{i}_{j}', field[i, j], None)
                saver = GetGridSerializer(data={'size': grid_count, 'x': i, 'y': j})
                saver.is_valid()
                saver.save(field[i, j])
        cache.set(f'grid_size_{grid_count}', field.shape, None)
        pil_img = pil_img.resize(size=(ceil(img.shape[1] / 2), ceil(img.shape[0] / 2)), resample=Image.BOX)
        img = np.array(pil_img)


def get_grid(img):
    field = np.ndarray(
        shape=(
            ceil(img.shape[0] / SMALLEST_SQUARE_SIZE),
            ceil(img.shape[1] / SMALLEST_SQUARE_SIZE)
        ),
        dtype=np.object
    )
    for i in range(field.shape[0]):
        for j in range(field.shape[1]):
            cur_img = img[i * SMALLEST_SQUARE_SIZE: (i + 1) * SMALLEST_SQUARE_SIZE,
                      j * SMALLEST_SQUARE_SIZE: (j + 1) * SMALLEST_SQUARE_SIZE]
            if cur_img.shape != (SMALLEST_SQUARE_SIZE, SMALLEST_SQUARE_SIZE, 3):
                to_out = np.zeros((SMALLEST_SQUARE_SIZE, SMALLEST_SQUARE_SIZE, 3))
                to_out[:cur_img.shape[0], :cur_img.shape[1]] = cur_img
                cur_img = to_out
            field[i, j] = cur_img.astype(dtype=np.uint8)
    return field


class GetGridSerializer(serializers.ModelSerializer):
    def get_proper_field(self):
        x = self.validated_data['x']
        y = self.validated_data['y']
        size = self.validated_data['size']
        grid = cache.get(f'level{size}_{x}_{y}')

        return grid

    def save(self, image):
        x = self.validated_data['x']
        y = self.validated_data['y']
        size = self.validated_data['size']

        fieldEntry = None
        try:
            fieldEntry = models.CurrentField.objects.get(x=x, size=size, y=y)
        except models.CurrentField.DoesNotExist:
            fieldEntry = models.CurrentField.objects.create(x=x, size=size, y=y)
        fieldEntry.image = image.tostring()
        fieldEntry.save()

    class Meta:
        model = models.CurrentField
        fields = ["x", "y", "size"]

class GridSize(serializers.Serializer):
    size = serializers.IntegerField()
# {"x": 1, "y": 1, "color": "#111111"}
