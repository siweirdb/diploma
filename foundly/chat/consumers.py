import json
from channels.generic.websocket import AsyncWebsocketConsumer
from items.models import User
from .models import ChatMessage
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_name"):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message")

            if not self.receiver_id or not message:
                return  # Ignore incomplete messages

            sender = self.user
            receiver = await database_sync_to_async(User.objects.get)(id=self.receiver_id)

            chat_message = await database_sync_to_async(ChatMessage.objects.create)(
                sender=sender, receiver=receiver, message=message
            )

            # Send message to the correct WebSocket room
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": str(sender.id),
                    "receiver_id": str(self.receiver_id),
                    "timestamp": str(chat_message.timestamp),
                },
            )
        except Exception as e:
            print(f"[WebSocket] Error processing message: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
