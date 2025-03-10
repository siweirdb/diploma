from django.urls import path
from .views import lobby, ChatListView, ChatDetailView


urlpatterns = [
    path('', lobby, name='test'),
    path("chats/", ChatListView.as_view(), name="chat-list"),
    path("chats/<uuid:user_id>/", ChatDetailView.as_view(), name="chat-detail"),
]

