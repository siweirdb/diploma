from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from items.views import CreateItemView

urlpatterns = [
    path('create/', CreateItemView.as_view(), name='create_item'),
    path('map/', CreateItemView.as_view(), name='create_item'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
