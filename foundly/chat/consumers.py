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
            self.room_name = f"chat_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data["sender_id"]
        receiver_id = data["receiver_id"]
        message = data["message"]

        sender = await database_sync_to_async(User.objects.get)(id=sender_id)
        receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)

        chat_message = await database_sync_to_async(ChatMessage.objects.create)(
            sender=sender, receiver=receiver, message=message
        )

        receiver_room_name = f"chat_{receiver_id}"

        await self.channel_layer.group_send(
            receiver_room_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": str(sender_id),
                "receiver_id": str(receiver_id),
                "timestamp": str(chat_message.timestamp),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
