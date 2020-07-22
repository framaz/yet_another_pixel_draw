"""Serializers. All logic is done here.

The drawing field is split into grids.
The basic idea of grids is to save computation time and internet connection bandwidth by giving the
user only the picture areas the user is working on/seing.

There are TOTAL_GIRD_LAYERS layers. Each layer corresponds to zoom level of the user. For example, if the
user zooms out for 64 times, it is not effective to give him the exact fields he sees. It's better to rescale the
picture on server side and then transfer him the rescaled image to save bandwidth.

Layer 0 grid is built on the exact pixels of the drawing field. Layer N grid is build on 2 ^ N times diminished
picture of drawing field.

Another technique to reduce the computation time is to store not only level 0 grid, but all the grids and to
change grids colors when a pixel is changed.

Grid operations may be separated into another class later for better project structuring.
"""
from json import loads
from math import ceil, floor

import numpy as np
from PIL import Image
from django.core.cache import cache
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from yet_another_pixel_draw import models
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db.models.query import QuerySet

# GRID_ELEMENT_SIZE is constant for the size of grid element
# 128 means any grid element is 128x128 pixels.
GRID_ELEMENT_SIZE = 128

# Shows the maximum number of grid layers
TOTAL_GIRD_LAYERS = 10


class PixelUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating pixels."""
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.date = None

    def save(self, user: User) -> None:
        """Updates a single pixel of the field.

        The update is done to all the grid layers so it might appear to be a bit slow.
        To keep the color precision, colors for all level calculated based on real_pixel - the real pixel value
        on 0 level. If color is changed to new_color, then the result on any layer can be evaluated by
        the following formula:

            color_in_grid += (new_color - real_pixel) / (4 ** grid_layer)

        Args:
            user: who updated the pixel.
        """
        x = self.validated_data['x']
        y = self.validated_data['y']
        color = self.validated_data['color']
        pixel = models.PixelHistory.objects.create(x=x, y=y, color=color, user=user)
        self.date = pixel.date
        self.validated_data['date'] = self.date
        color = np.array(loads(color))

        x_grid, x_in_grid = divmod(x, GRID_ELEMENT_SIZE)
        y_grid, y_in_grid = divmod(y, GRID_ELEMENT_SIZE)
        cur_grid = cache.get(f'level0_{x_grid}_{y_grid}')
        color_orig = cur_grid[x_in_grid, y_in_grid]

        self.validated_data['last_color'] = color_orig

        for grid_num in range(TOTAL_GIRD_LAYERS):
            x_grid, x_in_grid = divmod(x, GRID_ELEMENT_SIZE * 2 ** grid_num)
            y_grid, y_in_grid = divmod(y, GRID_ELEMENT_SIZE * 2 ** grid_num)
            cur_grid = cache.get(f'level{grid_num}_{x_grid}_{y_grid}')
            x_in_grid = floor(x_in_grid / (2 ** grid_num))
            y_in_grid = floor(y_in_grid / (2 ** grid_num))
            cur_grid[x_in_grid, y_in_grid] += ((color - color_orig) / (4 ** grid_num)).astype(np.uint8)
            cache.set(f'level{grid_num}_{x_grid}_{y_grid}', cur_grid, None)

    class Meta:
        model = models.PixelHistory
        fields = ['x', 'y', 'color']


class PixelHistorySerializer(serializers.Serializer):
    """Serializer to her all records from history model that are later than date."""
    date = serializers.DateTimeField()

    def get(self, json: bool = True) -> Union[str, QuerySet]:
        """Returns a serialized/nonserialized pixel history.

        TODO split the method to json serializer and queryset retriever.
        """
        if self.is_valid():
            date = self.validated_data['date']
            history_data = models.PixelHistory.objects.all().filter(date__gt=date).order_by('date')
            if json:
                history_serializer = SinglePixelHistorySerializer(history_data, many=True)
                res = JSONRenderer().render(history_serializer.data)
            else:
                res = history_data
            return res


class SinglePixelHistorySerializer(serializers.ModelSerializer):
    """Used to serialize single pixel history database record."""
    class Meta:
        model = models.PixelHistory
        fields = ['x', 'y', 'color', 'date']


class NewFieldSerializer(serializers.Serializer):
    """Serializer of new image for field and saves it into cache."""
    file = serializers.ImageField()

    def save(self, user: User, **kwargs) -> None:
        """Split image into grids and save it to cache.

        Args:
            user: the user, who uploaded new field. Not used now, will be used later.
        """
        pil_img = self.validated_data['file'].file
        pil_img = Image.open(pil_img)
        pil_img = pil_img.convert(mode="RGB")
        img = np.array(pil_img)
        img = img.transpose((1, 0, 2))

        pil_img = Image.fromarray(img)
        models.CurrentField.objects.all().delete()
        img_split_and_cache(img)


def img_split_and_cache(img: np.ndarray) -> None:
    """Split and cache an image into grids.

    TODO CHANGE TO JUST SPLIT, CACHE OUTSIDE
    Attributes:
        img: an image to split."""
    pil_img = Image.fromarray(img)
    for grid_count in range(TOTAL_GIRD_LAYERS):
        field = get_grid(img)
        for i in range(0, field.shape[0]):
            for j in range(0, field.shape[1]):
                cache.set(f'level{grid_count}_{i}_{j}', field[i, j], None)
                saver = GetGridElementSerializer(data={'size': grid_count, 'x': i, 'y': j})
                saver.is_valid()
                saver.save(field[i, j])
        cache.set(f'grid_size_{grid_count}', field.shape, None)
        pil_img = pil_img.resize(size=(ceil(img.shape[1] / 2), ceil(img.shape[0] / 2)), resample=Image.BOX)
        img = np.array(pil_img)


def get_grid(img: np.ndarray) -> np.ndarray:
    """Transforms a full image to a grid.

    If the image shapes are not divisible by GRID_ELEMENT_SIZE then the image is padded.

    Args:
        img: np.ndarray of the image.

    Returns:
        A grid array from the image.
    """
    field = np.ndarray(shape=(ceil(img.shape[0] / GRID_ELEMENT_SIZE),
                              ceil(img.shape[1] / GRID_ELEMENT_SIZE)),
                       dtype=np.object)

    for i in range(field.shape[0]):
        for j in range(field.shape[1]):
            cur_img = img[i * GRID_ELEMENT_SIZE: (i + 1) * GRID_ELEMENT_SIZE,
                      j * GRID_ELEMENT_SIZE: (j + 1) * GRID_ELEMENT_SIZE]

            # Padding

            if cur_img.shape != (GRID_ELEMENT_SIZE, GRID_ELEMENT_SIZE, 3):
                to_out = np.zeros((GRID_ELEMENT_SIZE, GRID_ELEMENT_SIZE, 3))
                to_out[:cur_img.shape[0], :cur_img.shape[1]] = cur_img
                cur_img = to_out
            field[i, j] = cur_img.astype(dtype=np.uint8)
    return field


class GetGridElementSerializer(serializers.ModelSerializer):
    """A serializer for working with grid elements(retrieval and changing)."""
    def get_grid_element_arr(self) -> np.ndarray:
        """Get grid element from cache.

        Returns:
            Grid element from cache.
        """
        x = self.validated_data['x']
        y = self.validated_data['y']
        size = self.validated_data['size']
        grid = cache.get(f'level{size}_{x}_{y}')

        return grid

    def save(self, image: np.ndarray) -> None:
        """Save/update grid element in the database.

        Args:
            image: grid element.
        """
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

# {"x": 1, "y": 1, "color": "#111111"}
