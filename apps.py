from django.apps import AppConfig
from django.core.cache import cache

class YetAnotherPixelDrawConfig(AppConfig):
    name = 'yet_another_pixel_draw'
    def ready(self):
        from .models import CurrentField
        from .serializers import MAX_GRID_SIZE, SMALLEST_SQUARE_SIZE, PixelHistorySerializer, img_split_and_cache
        from django.core.cache import cache
        from django.db.models import Min
        import numpy as np
        import json
        import matplotlib.pyplot as plt

        objects = CurrentField.objects.all().order_by('size')
        grid_size = []
        grids = np.ndarray(shape=(MAX_GRID_SIZE ,256, 256), dtype=object)

        for i in range(MAX_GRID_SIZE):
            grid_size.append([-1, -1])
        for obj in objects:
            if obj.x > grid_size[obj.size][0]:
                grid_size[obj.size][0] = obj.x
            if obj.y > grid_size[obj.size][1]:
                grid_size[obj.size][1] = obj.y
            grid = np.fromstring(obj.image, dtype=np.uint8, ).reshape((SMALLEST_SQUARE_SIZE, SMALLEST_SQUARE_SIZE, 3))
            grids[obj.size, obj.x, obj.y] = {'grid': grid, 'date': obj.date}

        for i in range(MAX_GRID_SIZE):
            for j in range(2):
                grid_size[i][j] += 1
            cache.set(f'grid_size_{i}', grid_size[i])

        min_date = CurrentField.objects.all().aggregate(Min('date'))
        min_date = min_date['date__min']
        serializer = PixelHistorySerializer(data={'date': min_date})
        serializer.is_valid()

        for pixel in serializer.get(json=False):
            x_grid, x_in_grid = divmod(pixel.x, SMALLEST_SQUARE_SIZE)
            y_grid, y_in_grid = divmod(pixel.y, SMALLEST_SQUARE_SIZE)
            grids[0, x_grid, y_grid]['grid'][x_in_grid][y_in_grid] = np.array(json.loads(pixel.color), dtype=np.uint8)

        shape = list(np.array(grid_size[0]) * SMALLEST_SQUARE_SIZE)
        shape.append(3)
        grid_image = np.zeros(shape=shape, dtype=np.uint8)

        for x in range(grid_size[0][0]):
            for y in range(grid_size[0][1]):
                cache.set(f'level0_{x}_{y}', grids[0][x][y]['grid'])
                grid_image[x * SMALLEST_SQUARE_SIZE: (x + 1) * SMALLEST_SQUARE_SIZE,
                           y * SMALLEST_SQUARE_SIZE: (y + 1) * SMALLEST_SQUARE_SIZE] = grids[0][x][y]['grid']

        # grid_image = grid_image.transpose(1, 0, 2)
        img_split_and_cache(grid_image)

