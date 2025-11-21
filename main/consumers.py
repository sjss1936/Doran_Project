import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import Message, Room

User = get_user_model()

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        username = text_data_json['username']

        # Save message to database
        try:
            user = User.objects.get(username=username)
            room, created = Room.objects.get_or_create(name=self.room_name)
            message = Message.objects.create(user=user, room=room, content=message_content)
            
            profile_picture_url = ''
            if hasattr(user, 'profile') and user.profile.profile_picture:
                profile_picture_url = user.profile.profile_picture.url

            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'username': user.username,
                    'profile_picture_url': profile_picture_url,
                    'timestamp': message.timestamp.isoformat(),
                    'message_id': message.id,
                }
            )
        except (User.DoesNotExist, Room.DoesNotExist) as e:
            print(f"Error saving message: {e}")
            # Optionally send an error back to the client
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to save message.'
            }))

    def chat_message(self, event):
        message = event['message']
        username = event['username']
        profile_picture_url = event['profile_picture_url']
        timestamp = event['timestamp']
        message_id = event['message_id']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'profile_picture_url': profile_picture_url,
            'timestamp': timestamp,
            'message_id': message_id,
        }))
