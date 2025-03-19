import json
from channels.generic.websocket import AsyncWebsocketConsumer
from users.models import User
from .models import ChatMessage
from channels.db import database_sync_to_async
import uuid
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.receiver_id = self.scope["url_route"]["kwargs"].get("receiver_id")  # Ensure receiver_id is retrieved

        if self.user.is_anonymous or not self.receiver_id:
            await self.close()
            return

        # Convert UUID to string if needed
        sender_id = str(self.user.id)
        receiver_id = str(self.receiver_id)

        # Ensure UUID is correctly formatted
        try:
            sender_id = uuid.UUID(sender_id)
            receiver_id = uuid.UUID(receiver_id)
        except ValueError:
            print("[WebSocket] Invalid UUID format")
            await self.close()
            return

        # Create a unique chat room name
        self.room_name = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

        # Join the room
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_name"):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
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

        elif bytes_data:
            # Optional: Handle binary data if needed
            print("Received binary data, but no handler is implemented.")

    async def chat_message(self, event):
        """ Send message event to WebSocket client """
        await self.send(text_data=json.dumps(event))
