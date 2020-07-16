from json import dumps

from django.core.cache import cache
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from yet_another_pixel_draw import serializers


# Create your views here.
class UpdatePixel(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        serializer = serializers.CurrentFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user)
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


class GetPixelFromGrid(APIView):
    def get(self, request, format=None):
        serializer = serializers.GetGridSerializer(data=request.data)
        if serializer.is_valid():
            field = serializer.get_proper_field()
            return Response(data=dumps(field.tolist()), status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGridSize(APIView):
    def get(self, request, format=None):
        res = {}
        for i in range(serializers.MAX_GRID_SIZE):
            res[i] = cache.get(f"grid_size_{i}")
            res[i] = [*(res[i])]
        return Response(data=dumps(res), status=status.HTTP_200_OK)


class FrontEnd(TemplateView):
    template_name = "yapd/front_end.html"
