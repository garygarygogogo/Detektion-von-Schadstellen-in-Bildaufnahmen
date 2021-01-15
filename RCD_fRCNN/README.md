# Faster R-CNN
## 环境配置：
* Python3.6或者3.7
* Pytorch1.6(注意：必须是1.6.0或以上，因为使用官方提供的混合精度训练1.6.0后才支持)
* pycocotools(Linux: pip install pycocotools;   
  Windows:pip install pycocotools-windows(不需要额外安装vs))
* Ubuntu或Centos(不建议Windows)
* 最好使用GPU训练
* 详细环境配置见```requirements.txt```

## 文件结构：
```
* ├── backbone: 特征提取网络，可以根据自己的要求选择
* ├── network_files: Faster R-CNN网络（包括Fast R-CNN以及RPN等模块）
* ├── train_utils: 训练验证相关模块（包括cocotools）
* ├── my_dataset.py: 自定义dataset用于读取VOC数据集
* ├── train_mobilenet.py: 以MobileNetV2做为backbone进行训练
* ├── train_resnet50_fpn.py: 以resnet50+FPN做为backbone进行训练
* ├── train_multi_GPU.py: 针对使用多GPU的用户使用
* ├── predict.py: 简易的预测脚本，使用训练好的权重进行预测测试
* └── pascal_voc_classes.json: pascal_voc标签文件
```


## 训练方法
* 确保提前准备好数据集
* 确保提前下载好对应预训练模型权重
* 若要训练mobilenetv2+fasterrcnn，直接使用train_mobilenet.py训练脚本
* 若要训练resnet50+fpn+fasterrcnn，直接使用train_resnet50_fpn.py训练脚本
* 若要使用多GPU训练，使用```python -m torch.distributed.launch --nproc_per_node=8 --use_env train_multi_GPU.py```指令,```nproc_per_node```参数为使用GPU数量
