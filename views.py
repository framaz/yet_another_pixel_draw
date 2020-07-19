from json import dumps

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.renderers import JSONRenderer

from yet_another_pixel_draw import serializers


# Create your views here.
class UpdatePixel(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        serializer = serializers.CurrentFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user)
            layer = get_channel_layer()
            async_to_sync(layer.group_send)('users', {
                'type': 'new_pixel',
                'content': JSONRenderer().render(serializer.validated_data)
            })
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadPicture(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = (FileUploadParser,)

    def put(self, request, format=None):
        serializer = serializers.NewFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


GRID_CACHING = 60

class GetHistory(APIView):
    def get(self, request):
        date = request.query_params['date']
        serializer = serializers.PixelHistorySerializer(data={'date': date})
        serializer = serializer
        res = serializer.get()
        return Response(res, status=status.HTTP_200_OK)



class GetPixelFromGrid(APIView):
    #@method_decorator(cache_page(GRID_CACHING))
    def get(self, request, size, x, y, format=None):
        serializer = serializers.GetGridSerializer(data={"x": x, "size": size, "y": y})
        if serializer.is_valid():
            field = serializer.get_proper_field()
            serializer.is_valid()
            serializer.save(field)
            return Response(data=dumps(field.tolist()), status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGridSize(APIView):
    #@method_decorator(cache_page(GRID_CACHING))
    def get(self, request, format=None):
        res = {}
        for i in range(serializers.MAX_GRID_SIZE):
            res[i] = cache.get(f"grid_size_{i}")
            res[i] = [*(res[i])]
        return Response(data=dumps(res), status=status.HTTP_200_OK)


class FrontEnd(TemplateView):
    template_name = "yapd/front_end.html"
