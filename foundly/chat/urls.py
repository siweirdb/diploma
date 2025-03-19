from django.urls import path
from .views import ChatListView, ChatDetailView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("chats/", ChatListView.as_view(), name="chat-list"),
    path("chat/<uuid:user_id>/", ChatDetailView.as_view(), name="chat-detail"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

