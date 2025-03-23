
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Category, Subcategory, Subsubcategory, Item
from .serializers import  CreateItemSerializer
from .serializers import CategorySerializer, SubcategorySerializer, SubsubcategorySerializer, ItemSerializer

from rest_framework import generics




class ItemDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ItemSerializer
    def get(self, request, *args, **kwargs):
        item_id = self.kwargs.get('id')
        item = Item.objects.get(id=item_id)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

class MapView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        items = Item.objects.all()

        return Response({
            'items': ItemSerializer(items, many=True).data,
        })



class CreateItemView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateItemSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        subcategories = Subcategory.objects.all()
        subsubcategories = Subsubcategory.objects.all()

        return Response({
            'category': CategorySerializer(categories, many=True).data,
            'subcategory': SubcategorySerializer(subcategories, many=True).data,
            'subsubcategory': SubsubcategorySerializer(subsubcategories, many=True).data,
        })










