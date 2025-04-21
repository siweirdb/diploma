import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
from PIL import Image
import io
from googletrans import Translator

class ImageClassifier:
    def __init__(self):
        self.model = MobileNetV2(weights='imagenet')
        self.translator = Translator()

    def predict_category(self, image_data):
        try:
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
            img = img.resize((224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            preds = self.model.predict(x)
            decoded_preds = decode_predictions(preds, top=5)[0]

            filtered_preds = []
            for class_id, class_name, confidence in decoded_preds:
                if confidence >= 0.80:
                    translated = self.translator.translate(class_name, src='en', dest='ru').text
                    filtered_preds.append({
                        "translated": translated,
                    })

            return filtered_preds

        except Exception as e:
            print(f"Prediction error: {e}")
            return []
