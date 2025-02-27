from ultralytics import YOLO

def load_model():
    model = YOLO("src/checkpoint/best.pt")  # Load trained YOLO model
    return model

def detect_skin_disease(model, image):
    results = model.predict(image)
    return results[0].plot()