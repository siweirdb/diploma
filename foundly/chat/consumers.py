import json
from channels.generic.websocket import AsyncWebsocketConsumer
from items.models import User
from .models import ChatMessage
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection"""
        print("WebSocket scope:", self.scope)
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_name = f"chat_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        if hasattr(self, "room_name"):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming messages"""
        try:
            data = json.loads(text_data)
            receiver_id = data.get("receiver_id")
            message = data.get("message")

            if not receiver_id or not message:
                return  # Ignore incomplete messages

            sender = self.user  # Ensure authenticated user is the sender
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)

            chat_message = await database_sync_to_async(ChatMessage.objects.create)(
                sender=sender, receiver=receiver, message=message
            )

            # Unique chat room for sender and receiver
            room_name = f"chat_{min(str(sender.id), str(receiver_id))}_{max(str(sender.id), str(receiver_id))}"

            await self.channel_layer.group_send(
                room_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": str(sender.id),
                    "receiver_id": str(receiver_id),
                    "timestamp": str(chat_message.timestamp),
                },
            )
        except Exception as e:
            print(f"[WebSocket] Error processing message: {e}")

    async def chat_message(self, event):
        """Sends messages to WebSocket"""
        await self.send(text_data=json.dumps(event))
