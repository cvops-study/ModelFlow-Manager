import os

import torch

model = torch.load("src/model/model.pt", map_location=torch.device('cpu'))
