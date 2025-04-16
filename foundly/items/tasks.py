from celery import shared_task
from .models import Item, ItemPhoto, Category, Subcategory, Subsubcategory
from .ai_model import ImageClassifier
import io

# Initialize the classifier when the module loads
classifier = ImageClassifier()


@shared_task(bind=True)
def process_item_photo(self, item_id, photo_id):
    try:
        item = Item.objects.get(id=item_id)
        item_photo = ItemPhoto.objects.get(id=photo_id)

        with item_photo.image.open('rb') as f:
            image_data = f.read()

        classifier = ImageClassifier()
        result = classifier.predict_category(image_data)

        if result['raw_predictions']:
            # Use the top prediction
            top_prediction = result['raw_predictions'][0]
            return f"AI predicted: {top_prediction['label']} (confidence: {top_prediction['confidence']:.2f})"

        return "No predictions made"
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        return f"Error processing photo: {str(e)}"