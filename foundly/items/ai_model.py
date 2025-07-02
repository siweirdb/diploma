import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
from PIL import Image
import io
import deepl
from googletrans import Translator

DEEPL_API_KEY = "457309eb-e004-401e-a119-652e4cd0f784:fx"

class ImageClassifier:
    def __init__(self):
        self.model = MobileNetV2(weights='imagenet')
        self.translator = deepl.Translator(DEEPL_API_KEY)

    def predict_category(self, image_data):
        try:

            img = Image.open(io.BytesIO(image_data)).convert('RGB')
            img = img.resize((224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)


            preds = self.model.predict(x)
            decoded_preds = decode_predictions(preds, top=1)[0]
            best_class_id, best_class_name, best_confidence = decoded_preds[0]

            readable_name = best_class_name.replace('_', ' ').strip()

            translated = self.translator.translate_text(
                readable_name, source_lang="EN", target_lang="RU"
            ).text

            return [{
                "translated": translated,
                "class_name": best_class_name,
                "confidence": float(best_confidence)
            }]

        except Exception as e:
            print(f"Prediction error: {e}")
            return []


