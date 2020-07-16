from django.shortcuts import render
from rest_framework.views import APIView
from yet_another_pixel_draw import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import FileUploadParser


# Create your views here.
class UpdatePixel(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        serializer = serializers.CurrentFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user)
            return Response(status=status.HTTP_201_CREATED)
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
        serializer = serializers.GetGridSerialiser(data=request.data)
        if serializer.is_valid():
            x = serializer.validated_data['x']
            y = serializer.validated_data['y']
            size = serializer.validated_data['size']


