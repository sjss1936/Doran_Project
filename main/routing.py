from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    # Path for 1-on-1 chat, using the other user's username
    path('ws/chat/<str:username>/', consumers.ChatConsumer.as_asgi()),
    # Path for user-specific notifications (like unread counts)
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]