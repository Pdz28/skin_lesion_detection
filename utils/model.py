from ultralytics import YOLO
from PIL import Image
import numpy as np

def load_model():
    model = YOLO("src/checkpoint/best.pt")  # Load trained YOLO model
    return model

def detect_skin_disease(model, image):
    results = model.predict(image)
    result_image = results[0].plot()
    result_image = Image.fromarray(result_image.astype('uint8'), 'RGB')
    return result_image
