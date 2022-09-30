import os
'''os.system("git clone https://github.com/ultralytics/yolov5")
os.system("pip install -qr yolov5/requirements.txt")
os.system("cd yolov5")
os.system("git reset --hard fbe67e465375231474a2ad80a4389efc77ecff99")'''
import numpy as np
print(np.sum(np.array([0,1,2,3])))
import torch
from IPython.display import Image, clear_output  # to display images
from roboflow import Roboflow
# from utils.downloads import attempt_download  # to download models/datasets
import yaml
from IPython.core.magic import register_line_cell_magic


# clear_output()
print('Setup complete. Using torch %s %s' % (
    torch.__version__, torch.cuda.get_device_properties(0) if torch.cuda.is_available() else 'CPU'))

rf = Roboflow(api_key="NHcztEwVoScyUkyO7sTo")
project = rf.workspace("university-of-amsterdam").project("jack")
dataset = project.version(1).download("yolov5")

os.system("cat jack-1/data.yaml")

with open(dataset.location + "/data.yaml", 'r') as stream:
    num_classes = str(yaml.safe_load(stream)['nc'])

os.system("python yolov5/train.py --rect --imgsz 1280 --batch 16 --epochs 200 --data jack-1/data.yaml --cfg "
          "yolov5/models/custom_yolov5s.yaml --weights '' --name yolov5s_results  --cache")
