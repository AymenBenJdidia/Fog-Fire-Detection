from ultralytics import YOLO
import cv2
import io
from PIL import Image
import numpy as np
import time

model = YOLO("fog/fire_model.pt") 

def detect_fire(image_bytes):
    start = time.time()

    # Convert bytes → OpenCV image
    img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # Run YOLO
    results = model(img, verbose=False)[0]

    fire = False
    conf = 0.0

    # Draw boxes
    for box in results.boxes:
        cls = int(box.cls[0])
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if cls == 0:  # fire class
            fire = True
            conf = max(conf, confidence)

            # Draw detection box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                img,
                f"FIRE {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

    # Show image on fog node
    cv2.imshow("Fog Fire Detection", img)
    cv2.waitKey(1)

    return {
        "fire": fire,
        "confidence": round(conf, 3),
        "message": "FIRE DETECTED!" if fire else "No fire",
        "processing_time": round(time.time() - start, 3)
    }
