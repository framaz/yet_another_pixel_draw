from django.shortcuts import render
from rest_framework.views import APIView
from yet_another_pixel_draw import serializers
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class UpdatePixel(APIView):
    def put(self, request, format=None):
        serializer = serializers.CurrentFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)