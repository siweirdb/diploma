from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CreateItemView, MapView, ItemDetailView, ItemHistoryView



urlpatterns = [
    path('create/', CreateItemView.as_view(), name='create_item'),
    path('map/', MapView.as_view(), name='map'),
    path('<uuid:id>/',ItemDetailView.as_view(), name='item_detail'),
    path('history/',ItemHistoryView.as_view(), name='item_history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
