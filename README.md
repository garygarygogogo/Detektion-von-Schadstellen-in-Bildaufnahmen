# Detektion-von-Schadstellen-in-Bildaufnahmen
DCAITI Project--WS20/21

1.You can train your own version or download the weight files from https://drive.google.com/drive/folders/1gFtHe5ZCGfZnrlUW-Pua1UCJY1JM6ZFR?usp=sharing
and put the .pth files into the corresponding folder.

2.For the develop of rcnn, you need to set the fasterrcnn_resnet50_fpn_coco.pth to ./RCD_FRCNN/backbone.

3.For the deployment on android devices, please see ./RCD_nanodet/demo_android_ncnn/README.md.

4.Download the dataset: https://github.com/sekilab/RoadDamageDetector

Reference:

Nanodet:https://github.com/RangiLyu/nanodet.git

EfficientDet:https://github.com/mahdi65/roadDamageDetection2020

Yolo:https://github.com/ultralytics/yolov5.git
