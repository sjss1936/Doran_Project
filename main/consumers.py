import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        # The other user's username is expected from the URL route.
        # This consumer is for 1-on-1 chat.
        self.other_username = self.scope['url_route']['kwargs']['username']
        
        # Create a consistent, unique room name for the two users.
        sorted_usernames = sorted([self.user.username, self.other_username])
        self.room_group_name = f"chat_{sorted_usernames[0]}_{sorted_usernames[1]}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # Mark messages as read upon connection
        await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json['message']
        except (json.JSONDecodeError, KeyError):
            await self.send_error("Invalid data format.")
            return

        if not message_content:
            return

        # Get receiver user object
        receiver = await self.get_user(self.other_username)
        if not receiver:
            await self.send_error("Receiver user not found.")
            return

        # Save message to database
        new_message = await self.save_message(self.user, receiver, message_content)

        # Prepare user-specific channel names for notification
        sender_channel = f"user_{self.user.id}"
        receiver_channel = f"user_{receiver.id}"

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message.content,
                'sender': self.user.username,
                'timestamp': new_message.timestamp.isoformat()
            }
        )
        
        # Send a notification to the receiver to update their message count
        await self.channel_layer.group_send(
            receiver_channel,
            {
                'type': 'unread_message_count_update'
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))
    
    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    @database_sync_to_async
    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        return Message.objects.create(sender=sender, receiver=receiver, content=content)

    @database_sync_to_async
    def mark_messages_as_read(self):
        # Mark messages sent by the other user to the current user as read
        Message.objects.filter(
            sender__username=self.other_username, 
            receiver=self.user, 
            is_read=False
        ).update(is_read=True)

# This new consumer will handle user-specific notifications like unread counts
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Handler for when a new unread notification is created
    async def unread_notification_count_update(self, event):
        count = await self.get_unread_notification_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_notification_update',
            'count': count
        }))
        
    # Handler for when a new unread message is received
    async def unread_message_count_update(self, event):
        count = await self.get_unread_message_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_message_update',
            'count': count
        }))

    @database_sync_to_async
    def get_unread_notification_count(self):
        return self.user.notifications.filter(is_read=False).count()

    @database_sync_to_async
    def get_unread_message_count(self):
        return Message.objects.filter(receiver=self.user, is_read=False).count()
