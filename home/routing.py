from django.urls import path

from home import consumers

websocket_urlpatterns = [
    path('ws/speech/', consumers.TestConsumer.as_asgi()),
    path('ws/live/', consumers.LiveConsumer.as_asgi()),
    path('ws/oyqiz/', consumers.OyqizConsumer.as_asgi())
]
