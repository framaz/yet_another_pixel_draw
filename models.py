from django.contrib.auth.models import User
from django.db import models


class PixelHistory(models.Model):
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

