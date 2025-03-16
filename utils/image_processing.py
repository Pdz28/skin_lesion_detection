import cv2
import numpy as np
from PIL import Image

def preprocess_image(image):
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (640, 640))  # Resize to match YOLO input size
    return image
