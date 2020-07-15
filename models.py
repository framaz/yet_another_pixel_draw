from django.db import models


class PixelHistory(models.Model):
    x = models.IntegerField(null=False)
    y = models.IntegerField(null=False)
    color = models.CharField(max_length=7, default="#000000")
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


class CurrentField(models.Model):
    x = models.IntegerField(null=False)
    y = models.IntegerField(null=False)
    color = models.CharField(max_length=7, default="#000000")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['x', 'y'], name="Primary Key"),
        ]
