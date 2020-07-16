from rest_framework import serializers
from yet_another_pixel_draw import models
from django.core.exceptions import ObjectDoesNotExist


class CurrentFieldSerializer(serializers.ModelSerializer):
    def save(self, user):
        x = self.validated_data['x']
        y = self.validated_data['y']
        color = self.validated_data['color']
        models.PixelHistory.objects.create(x=x, y=y, color=color, user=user)
        try:
            res = models.CurrentField.objects.all().filter(x=x, y=y)[0]
            self.update(res, validated_data=self.validated_data)
        except ObjectDoesNotExist:
            super().save()

    class Meta:
        model = models.CurrentField
        fields = ['x', 'y', 'color']


class GetGridSerialiser(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    size = serializers.IntegerField()

# {"x": 1, "y": 1, "color": "#111111"}
