from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatListSerializer
from items.models import User


def lobby(request):
    return render(request, 'lobby.html')

class ChatListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        chat_users = User.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_messages__sender=user)
        ).distinct()

        serializer = ChatListSerializer(chat_users, many=True)
        return Response(serializer.data)


class ChatDetailView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.kwargs.get("user_id")

        return ChatMessage.objects.filter(
            (Q(sender=user) & Q(receiver__id=other_user_id)) |
            (Q(sender__id=other_user_id) & Q(receiver=user))
        ).order_by("timestamp")
