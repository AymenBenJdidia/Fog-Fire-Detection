# fog/fire_detector.py
from ultralytics import YOLO
import cv2
import time
import numpy as np
from PIL import Image
import io

# Load the YOLO model once (important!)
model = YOLO("fog/fire_model.pt")

def detect_fire(image_bytes) -> dict:
    """
    image_data: base64 string OR file path depending on how you call it.
    Returns detection results.
    """

    start_time = time.time()

    # Convert image_data (path) → image array
    img = Image.open(io.BytesIO(image_bytes))
    if img is None:
        return {
            "fire": False,
            "confidence": 0.0,
            "message": "Invalid image input",
            "timestamp": time.time()
        }

    # Run detection
    results = model(img, stream=True)

    fire_detected = False
    best_confidence = 0.0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            # Your model has only 1 class: 'fire'
            if cls == 0 and conf > best_confidence:
                best_confidence = conf
                fire_detected = True

    return {
        "fire": fire_detected,
        "confidence": round(best_confidence, 3),
        "message": "FIRE DETECTED!" if fire_detected else "No fire",
        "timestamp": start_time
    }
