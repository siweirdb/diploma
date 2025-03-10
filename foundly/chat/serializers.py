from rest_framework import serializers
from .models import ChatMessage
from items.models import User

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "receiver", "message", "timestamp"]


class ChatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]