#dependencies 
# pip install -q git+https://github.com/huggingface/transformers.git
# pip install -q timm



# pytorch
import pandas as pd
import torch

#hugginface
from transformers import TableTransformerForObjectDetection
from transformers import DetrImageProcessor

# image loader
from PIL import Image

# pour affichage du résultat
import matplotlib.pyplot as plt


# variables et fonctions globales
# colors for visualization
COLORS = [[0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125],
          [0.494, 0.184, 0.556], [0.466, 0.674, 0.188], [0.301, 0.745, 0.933]]

# fonction affichage résultats
def plot_results(model, pil_img, scores, labels, boxes):
    plt.figure(figsize=(16,10))
    plt.imshow(pil_img)
    ax = plt.gca()
    colors = COLORS * 100
    for score, label, (xmin, ymin, xmax, ymax),c  in zip(scores.tolist(), labels.tolist(), boxes.tolist(), colors):
        ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                   fill=False, color=c, linewidth=3))
        text = f'{model.config.id2label[label]}: {score:0.2f}'
        ax.text(xmin, ymin, text, fontsize=15,
                bbox=dict(facecolor='yellow', alpha=0.5))
    plt.axis('off')
    plt.show()
    # rescale bounding boxes




def ImagePreprocessing(image):
  # Let's first apply the regular image preprocessing using DetrImageProcessor. 
  # The feature extractor will resize the image (minimum size = 800, max size = 1333), and normalize it across the channels using the ImageNet mean and standard deviation.
  feature_extractor = DetrImageProcessor()
  encoding = feature_extractor(image, return_tensors="pt")
  encoding.keys()
  print(encoding['pixel_values'].shape)
  return feature_extractor, encoding 



def modelFindTable(image) :
  feature_extractor, encoding = ImagePreprocessing(image)
  # using model 
  model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-detection")
  # désactiver les calculs de gradient
  with torch.no_grad():
    outputs = model(**encoding)
  width, height = image.size
  results = feature_extractor.post_process_object_detection(outputs, threshold=0.7, target_sizes=[(height, width)])[0]
  plot_results(model, image, results['scores'], results['labels'], results['boxes'])



def modelFindCellsInImagePng(image) :
  feature_extractor, encoding = ImagePreprocessing(image)
  model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-structure-recognition")
  with torch.no_grad():
    outputs = model(**encoding)

  target_sizes = [image.size[::-1]]
  results = feature_extractor.post_process_object_detection(outputs, threshold=0.6, target_sizes=target_sizes)[0]
  print(results)
  plot_results(model, image, results['scores'], results['labels'], results['boxes'])




###################### MAIN ########################
# Charger l'image représentant un tableau "excel"
document_image_path = "C:\\Users\\gael.jaunin\\OneDrive - Naldeo\\Documents\\1.NDC\\1-NALDIA\\v0\\auth\\chatapp\\sharepoint\\datasets\\tableauTest.png"
document_csv_path = "C:\\Users\\gael.jaunin\\OneDrive - Naldeo\\Documents\\1.NDC\\1-NALDIA\\v0\\auth\\chatapp\\sharepoint\\datasets\\tableauTest.csv"

image = Image.open(document_image_path).convert("RGB")
width, height = image.size
# image.resize((int(width*0.5), int(height*0.5)))
modelFindCellsInImagePng(image)