from torch import nn
import pandas as pd
import io
import PIL.Image as Image
import torch
import torchvision
from transformers import SegformerFeatureExtractor, SegformerForSemanticSegmentation
from datetime import datetime

print(torch.__version__)
print(torchvision.__version__)

OBJECT_LABELS = pd.read_csv('./objects_model/OBJECT_LABELS.csv')
MODEL_NAME = "nvidia/segformer-b5-finetuned-ade-640-640"

feature_extractor = SegformerFeatureExtractor.from_pretrained(MODEL_NAME)
model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


class ModelLogic:
    def __init__(self):
        pass

    def model_specific_logic(self, image_bytes):
        started_time = datetime.now()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        pixel_values = feature_extractor(image, return_tensors="pt").pixel_values.to(device)
        predict = model(pixel_values)
        logits = nn.functional.interpolate(predict.logits.detach().cpu(),
                                           size=image.size[::-1],  # (height, width)
                                           mode='bilinear',
                                           align_corners=False)

        seg = logits.argmax(dim=1)[0]
        label_name = OBJECT_LABELS['name']
        labels = seg.unique()

        tags = []
        for label in labels:
            tags.append(label_name[int(label)])

        ended_time = datetime.now()
        print(f'TIME:{ended_time - started_time}')

        return [{'name': tag} for tag in tags]
