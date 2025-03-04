from ultralytics import YOLO
from PIL import Image, ImageDraw
import cv2
import numpy as np

def load_model():
    model = YOLO("src/checkpoint/skin_v4_yolo10.pt")  # Load trained YOLO model
    return model

def detect_skin_disease(model, image):
    # Predict without showing labels
    results = model.predict(
        source=image,
        conf=0.18,
        iou=0.8,
        show=False,
        show_labels=False,
        show_conf=False,
    )
    
    # Create PIL image from numpy array
    result_image_0 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_array = np.array(result_image_0)
    result_image = Image.fromarray(img_array)
    draw = ImageDraw.Draw(result_image)
    
    # Draw boxes without labels
    predictions = []
    has_detection = False

    for r in results:
        if len(r.boxes) > 0:
            has_detection = True
            for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
                # Draw rectangle
                box = box.cpu().numpy()
                draw.rectangle(
                    [(box[0], box[1]), (box[2], box[3])],
                    outline='red',
                    width=2
                )
                
                # Store prediction data
                predictions.append({
                    'box': box.tolist(),
                    'class': int(cls.item()),
                    'confidence': float(conf.item())
                })
    
    status = {
        "has_detection": has_detection,
        "message": "Warning: Detect skin lesion" if has_detection else "Your skin completely normal"
    }
    return result_image, predictions, status