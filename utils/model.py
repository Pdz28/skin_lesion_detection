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
    
    # Debug: kiểm tra kết quả từ model
    print(f"Number of results: {len(results)}")
    
    # Create PIL image from numpy array
    result_image_0 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_array = np.array(result_image_0)
    result_image = Image.fromarray(img_array)
    draw = ImageDraw.Draw(result_image)
    
    # Draw boxes without labels
    predictions = []
    has_detection = False
    print(f"Initial has_detection: {has_detection}")

    for i, r in enumerate(results):
        print(f"Result {i}: Found {len(r.boxes)} boxes")
        if len(r.boxes) > 0:
            print("Setting has_detection = True")
            has_detection = True
            for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
                # Draw rectangle
                box = box.cpu().numpy()
                draw.rectangle(
                    [(box[0], box[1]), (box[2], box[3])],
                    outline='red',
                    width=2
                )
                print(f"Box drawn at {box}, class={int(cls.item())}, conf={float(conf.item())}")
                
                # Store prediction data
                predictions.append({
                    'box': box.tolist(),
                    'class': int(cls.item()),
                    'confidence': float(conf.item())
                })
    
    print(f"Final has_detection: {has_detection}")
    print(f"Number of predictions: {len(predictions)}")
    
    status = {
        "has_detection": has_detection,
        "message": "Warning: Detect skin lesion" if has_detection else "Your skin completely normal"
    }
    print(f"Final status: {status}")
    return result_image, predictions, status