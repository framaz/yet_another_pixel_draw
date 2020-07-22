from django.contrib.auth.models import User
from django.db import models


class PixelHistory(models.Model):
    """Stores logs of pixel changes.

    Attributes:
        x: integer, x coordinate of changed pixel.
        y: integer, y coordinate of changed pixel.
        color: string in format "[a, b, c]", an rgb color code for new pixel color
        date: datetime, when pixel was placed.
        user: User, who placed the pixel.

    Constraints:
        x > 0.
        y > 0.
    """
    x = models.IntegerField(null=False)
    y = models.IntegerField(null=False)
    color = models.CharField(default="[0, 0, 0]", max_length=20)
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(x__gte=0), name="x_gte_0"),
            models.CheckConstraint(check=models.Q(y__gte=0), name="y_gte_0"),
        ]


class CurrentField(models.Model):
    """Current field grid information stored as grid elements.

    Attributes:
        x: int, x coordinate of element in the field grid.
        y: int, y coordinate of element in the field grid.
        size: int, grid layer. TODO deprecate size from database.
        image: binary string, The grid element's picture. Note that it is stored as BinaryField.
        date: when the grid was updated.

    Constraints:
        x, y, size - unique, there possible to be no grid elements with same coords and layer.

    Indexes:
        x, y, size - made as an index as x, y, size is a common get pattern.
    """
    x = models.IntegerField(null=False)
    y = models.IntegerField(null=False)
    size = models.IntegerField(null=False)
    image = models.BinaryField(max_length=10000)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['x', 'y', 'size'], name="uniquity", )
        ]
        indexes = [
            models.Index(fields=['x', 'y', 'size'], name="index")
        ]

