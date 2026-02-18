import torch.nn as nn

class CNNFaultDetector(nn.Module):
    def __init__(self):
        super().__init__()

        self.net = nn.Sequential(
            nn.Conv2d(1, 16, 3),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(16 * 111 * 111, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)
