from rest_framework import status, permissions
from .models import Item
from .serializers import  CreateItemSerializer
from .serializers import CategorySerializer, SubcategorySerializer, SubsubcategorySerializer, ItemSerializer

from rest_framework import generics

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ImageAnalysisSerializer
from .ai_model import ImageClassifier
from .models import Category, Subcategory, Subsubcategory


class AnalyzeImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        image_file = request.FILES['image']
        classifier = ImageClassifier()

        try:
            image_data = image_file.read()
            predictions = classifier.predict_category(image_data)
            return Response({"predictions": predictions})

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ItemHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

class ItemDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ItemSerializer
    def get(self, request, *args, **kwargs):
        item_id = self.kwargs.get('id')
        item = Item.objects.get(id=item_id)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

class MapView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ItemSerializer
    def get_queryset(self):
        return Item.objects.all()




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










