# src/quality_defect/train_defect.py
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from torch import nn
from PIL import Image
from pathlib import Path
import os

# -----------------------------
# Config
# -----------------------------
data_dir = Path("C:/Projects/SGMAS/data/images/quality/DEFECTS")
model_path = "C:/Projects/SGMAS/data/models/defect_model_weights.pth"
os.makedirs(os.path.dirname(model_path), exist_ok=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
num_epochs = 2

# -----------------------------
# Dataset with dummy boxes
# -----------------------------
class DefectDataset(Dataset):
    def __init__(self, transform=None):
        self.transform = transform
        self.images = list(data_dir.glob("*.jpg")) + list(data_dir.glob("*.jpeg")) + list(data_dir.glob("*.png"))
        print(f"Found {len(self.images)} defect images")
        if len(self.images) == 0:
            raise ValueError(f"No images found in {data_dir}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = Image.open(self.images[idx]).convert("RGB")
        target = {}
        target["boxes"] = torch.tensor([[10,10,100,100]], dtype=torch.float32)  # dummy box
        target["labels"] = torch.tensor([1], dtype=torch.int64)
        if self.transform:
            img = self.transform(img)
        return img, target

# -----------------------------
# Transform
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

dataset = DefectDataset(transform=transform)
data_loader = DataLoader(dataset, batch_size=1, shuffle=True, collate_fn=lambda x: tuple(zip(*x)))

# -----------------------------
# Model
# -----------------------------
model = models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
num_classes = 2  # 1 defect + background
in_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = models.detection.faster_rcnn.FastRCNNPredictor(in_features, num_classes)
model = model.to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

# -----------------------------
# Training loop
# -----------------------------
for epoch in range(num_epochs):
    model.train()
    for imgs, targets in data_loader:
        imgs = list(img.to(device) for img in imgs)
        targets = [{k:v.to(device) for k,v in t.items()} for t in targets]
        loss_dict = model(imgs, targets)
        losses = sum(loss for loss in loss_dict.values())
        optimizer.zero_grad()
        losses.backward()
        optimizer.step()
    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {losses.item():.4f}")

# -----------------------------
# Save weights only
# -----------------------------
torch.save(model.state_dict(), model_path)
print(f"Defect model weights saved at {model_path}")
