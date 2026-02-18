import torch
from torchvision import datasets, transforms, models
from torch import nn, optim
from torch.utils.data import DataLoader
import os

QUALITY_CLASSES = ["DEFECT", "GOOD"]

DATA_DIR = "data/images/quality"
MODEL_PATH = "data/models/quality_model_weights.pth"

def train_quality_model(epochs=5):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    dataset = datasets.ImageFolder(DATA_DIR, transform=transform)
    loader = DataLoader(dataset, batch_size=8, shuffle=True)

    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, 2)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)

    model.train()
    for epoch in range(epochs):
        for images, labels in loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch+1}/{epochs} completed")

    os.makedirs("data/models", exist_ok=True)
    torch.save(model.state_dict(), MODEL_PATH)
    print("✅ Model saved:", MODEL_PATH)
if __name__ == "__main__":
    train_quality_model()
