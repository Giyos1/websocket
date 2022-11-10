import json
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import TextSerializer
from rest_framework.response import Response


# Create your views here.

class Home(APIView):
    def post(self, request):
        serializer = TextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.data.get('text')
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.send)('audio', {
            'type': 'process',
            'text': text
        })

        return Response(data={'message': "ok"}, status=200)
