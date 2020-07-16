from django.shortcuts import render
from rest_framework.views import APIView
from yet_another_pixel_draw import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

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