from django.db import models
from django.contrib.auth.models import User


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


class FieldHistory(models.Model):
    field = models.BinaryField()
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=True, default=None, on_delete=models.DO_NOTHING)

