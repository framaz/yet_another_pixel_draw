"""Views.

Mostly just apis. No logic is here, logic is delegated to serializers.
"""

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
    """Api for pixel updating.

    Needs the user to be authenticated."""
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        """Update a pixel.

        Also notifies all websocket clients about pixel change.

        Returns:
            Operation code status.
        """
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
    """New field picture upload api.

    Accessible only by admin. Requires a file passed.
    """
    permission_classes = [IsAdminUser]
    parser_classes = (FileUploadParser,)

    def put(self, request, format=None):
        """Upload new field picture.

        Returns:
            Operation code status.
            """
        serializer = serializers.NewFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request.user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


GRID_CACHING = 60


class GetHistory(APIView):
    """Get pixel change from date history api.

    Not used now but might become useful if grid elements become cachable.
    """
    def get(self, request):
        """Get pixel history from date.

        Returns:
            JSON-formatted pixel change history or error code.
                Example: {"x": 1, "y": 2, "color": "[230, 255, 255]", "date": "20050809T183142+03"}
        """
        date = request.query_params['date']
        serializer = serializers.PixelHistorySerializer(data={'date': date})
        serializer = serializer
        res = serializer.get()
        return Response(res, status=status.HTTP_200_OK)


class GetGridElement(APIView):
    """Api for getting grid elements.

    Now it's not cachable."""
    # @method_decorator(cache_page(GRID_CACHING))
    def get(self, request, size: int, x: int, y: int, format=None):
        """Get grid element by it's layer and (x, y) coordinates."""
        serializer = serializers.GetGridSerializer(data={"x": x, "size": size, "y": y})
        if serializer.is_valid():
            field = serializer.get_proper_field()
            serializer.is_valid()
            serializer.save(field)
            return Response(data=dumps(field.tolist()), status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGridSize(APIView):
    """Api for getting grid sizes.

    It does not explicitly list all available grid elements with links to them, but it is easy to find
    by the grid sizes.

    Now it's not cachable.
    """
    # @method_decorator(cache_page(GRID_CACHING))
    def get(self, request, format=None):
        """Get grid sizes."""
        res = {}
        for i in range(serializers.MAX_GRID_SIZE):
            res[i] = cache.get(f"grid_size_{i}")
            res[i] = [*(res[i])]
        return Response(data=dumps(res), status=status.HTTP_200_OK)


class FrontEnd(TemplateView):
    """Frontend view, just renders frontend template."""
    template_name = "yapd/front_end.html"
