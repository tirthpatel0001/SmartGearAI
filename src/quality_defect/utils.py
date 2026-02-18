import torch
from torchvision import transforms
from PIL import Image

def load_image(image_path, size=(224,224)):
    img = Image.open(image_path).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406], [0.229,0.224,0.225])
    ])
    return transform(img).unsqueeze(0)

def tensor_to_image(tensor):
    img = tensor.squeeze().permute(1,2,0).detach().numpy()
    img = (img * 255).astype('uint8')
    return Image.fromarray(img)
