import torch
import torchvision
import cv2
import numpy as np
from PIL import Image
from torchvision import transforms
from torch.serialization import add_safe_globals

# ------------------------------------------------------------------
# 🔐 PyTorch 2.6+ SAFE GLOBALS (IMPORTANT)
# ------------------------------------------------------------------
# We explicitly trust FasterRCNN because this is OUR trained model
add_safe_globals([
    torchvision.models.detection.faster_rcnn.FasterRCNN
])

# ------------------------------------------------------------------
# 📦 LOAD IMAGE DEFECT MODEL
# ------------------------------------------------------------------
def load_defect_model(model_path: str, device: str = None):
    """
    Loads a Faster R-CNN defect detection model safely.

    Args:
        model_path (str): Path to .pth model file
        device (str): 'cpu' or 'cuda'

    Returns:
        model (torch.nn.Module)
        device (torch.device)
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    device = torch.device(device)

    model = torch.load(model_path)  # safe because of add_safe_globals
    model.to(device)
    model.eval()

    return model, device


# ------------------------------------------------------------------
# 🔍 IMAGE DEFECT DETECTION
# ------------------------------------------------------------------
def detect_defects(
    image_path: str,
    model,
    device,
    confidence_threshold: float = 0.5
):
    """
    Runs defect detection on an image.

    Args:
        image_path (str): Path to image
        model: Loaded Faster R-CNN model
        device: torch.device
        confidence_threshold (float): Min confidence for detections

    Returns:
        result_image (np.ndarray): Image with bounding boxes
        detections (list): List of detected defects
    """

    # Load image
    image = Image.open(image_path).convert("RGB")

    transform = transforms.Compose([
        transforms.ToTensor()
    ])

    img_tensor = transform(image).unsqueeze(0).to(device)

    # Inference
    with torch.no_grad():
        outputs = model(img_tensor)[0]

    boxes = outputs["boxes"].cpu().numpy()
    scores = outputs["scores"].cpu().numpy()
    labels = outputs["labels"].cpu().numpy()

    # Convert image for OpenCV
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    detections = []

    for box, score, label in zip(boxes, scores, labels):
        if score < confidence_threshold:
            continue

        x1, y1, x2, y2 = map(int, box)

        # Draw bounding box
        cv2.rectangle(img_cv, (x1, y1), (x2, y2), (0, 255, 0), 2)

        text = f"Defect {label} ({score:.2f})"
        cv2.putText(
            img_cv,
            text,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        detections.append({
            "label": int(label),
            "confidence": float(score),
            "bbox": [x1, y1, x2, y2]
        })

    return img_cv, detections
