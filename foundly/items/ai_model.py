import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
from PIL import Image
import io


class ImageClassifier:
    def __init__(self):
        self.model = MobileNetV2(weights='imagenet')

    def predict_category(self, image_data):
        try:
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
            img = img.resize((224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            preds = self.model.predict(x)
            decoded_preds = decode_predictions(preds, top=3)[0]

            # Return only raw predictions without any mapping
            return [
                {
                    "class_id": class_id,  # ImageNet class ID (e.g., 'n03180011')
                    "class_name": class_name,  # Original ImageNet class name
                    "confidence": float(confidence)
                }
                for (class_id, class_name, confidence) in decoded_preds
            ]

        except Exception as e:
            print(f"Prediction error: {e}")
            return []