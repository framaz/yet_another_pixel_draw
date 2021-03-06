from django.apps import AppConfig
from django.core.cache import cache


class YetAnotherPixelDrawConfig(AppConfig):
    name = 'yet_another_pixel_draw'

    def ready(self):
        """Load the pixel field from db to caches.

        Note that only the 0 layer grid is loaded, all other levels are rebuild from scratch.
        As there may be that a field grid was saved before new pixels were added to it, new pixels should
        be added.
        Also don't move the imports to the top of the file as django throws exceptions if you try to
        import models before django is fully started.

        """
        from .models import CurrentField
        from .serializers import TOTAL_GIRD_LAYERS, GRID_ELEMENT_SIZE, PixelHistorySerializer, img_split_and_cache
        from django.core.cache import cache
        from django.db.models import Min
        import numpy as np
        import json

        objects = CurrentField.objects.all().order_by('size')
        grid_size = []
        grids = np.ndarray(shape=(TOTAL_GIRD_LAYERS, 256, 256), dtype=object)

        # loading the 0 layer from db
        # TODO only 0 layer

        for i in range(TOTAL_GIRD_LAYERS):
            grid_size.append([-1, -1])
        for obj in objects:
            if obj.x > grid_size[obj.size][0]:
                grid_size[obj.size][0] = obj.x
            if obj.y > grid_size[obj.size][1]:
                grid_size[obj.size][1] = obj.y
            grid = np.fromstring(obj.image, dtype=np.uint8, ).reshape((GRID_ELEMENT_SIZE, GRID_ELEMENT_SIZE, 3))
            grids[obj.size, obj.x, obj.y] = {'grid': grid, 'date': obj.date}

        # calculating grid sizes

        for i in range(TOTAL_GIRD_LAYERS):
            for j in range(2):
                grid_size[i][j] += 1
            cache.set(f'grid_size_{i}', grid_size[i])

        # Adding newer pixels to layer 0 grids

        min_date = CurrentField.objects.all().aggregate(Min('date'))
        min_date = min_date['date__min']
        serializer = PixelHistorySerializer(data={'date': min_date})
        serializer.is_valid()

        for pixel in serializer.get(json=False):
            x_grid, x_in_grid = divmod(pixel.x, GRID_ELEMENT_SIZE)
            y_grid, y_in_grid = divmod(pixel.y, GRID_ELEMENT_SIZE)
            grids[0, x_grid, y_grid]['grid'][x_in_grid][y_in_grid] = np.array(json.loads(pixel.color), dtype=np.uint8)

        # recalculating all other grids

        shape = list(np.array(grid_size[0]) * GRID_ELEMENT_SIZE)
        shape.append(3)
        grid_image = np.zeros(shape=shape, dtype=np.uint8)

        for x in range(grid_size[0][0]):
            for y in range(grid_size[0][1]):
                cache.set(f'level0_{x}_{y}', grids[0][x][y]['grid'])
                grid_image[x * GRID_ELEMENT_SIZE: (x + 1) * GRID_ELEMENT_SIZE,
                y * GRID_ELEMENT_SIZE: (y + 1) * GRID_ELEMENT_SIZE] = grids[0][x][y]['grid']

        # grid_image = grid_image.transpose(1, 0, 2)
        img_split_and_cache(grid_image)
