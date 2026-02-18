import torch
from torchvision import transforms
from PIL import Image
import torchvision.models as models

QUALITY_CLASSES = ["DEFECT", "GOOD"]

def load_quality_model(model_path):
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, 2)

    state_dict = torch.load(model_path, map_location="cpu", weights_only=True)
    model.load_state_dict(state_dict)

    model.eval()
    return model

def predict_quality(image_path, model):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        _, pred = torch.max(outputs, 1)

    return QUALITY_CLASSES[pred.item()]
