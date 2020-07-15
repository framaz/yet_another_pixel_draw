from rest_framework import serializers
from yet_another_pixel_draw import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import caches

class CurrentFieldSerializer(serializers.ModelSerializer):
    def save(self):
        try:
            x = self.validated_data['x']
            y = self.validated_data['y']
            res = models.CurrentField.objects.all().filter(x=x, y=y)[0]
            self.update(res, validated_data=self.validated_data)
        except ObjectDoesNotExist:
            super().save()


    class Meta:
        model = models.CurrentField
        fields = ['x', 'y', 'color']

# {"x": 1, "y": 1, "color": "#111111"}