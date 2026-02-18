# src/quality_defect/predict_defect.py
import torch
from torchvision import models, transforms
from PIL import Image

transform = transforms.Compose([
    transforms.ToTensor()
])

def load_defect_model(path="C:/Projects/SGMAS/data/models/defect_model_weights.pth"):
    model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    num_classes = 2  # 1 defect + background
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = models.detection.faster_rcnn.FastRCNNPredictor(in_features, num_classes)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model

def predict_defects(img_path, model, device="cpu"):
    img = Image.open(img_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)
    model.to(device)
    with torch.no_grad():
        detections = model(x)[0]
    defects = []
    for box, score, label in zip(detections['boxes'], detections['scores'], detections['labels']):
        if score > 0.5:
            defects.append({
                "box": box.tolist(),
                "score": score.item(),
                "label": label.item()
            })
    return defects
