# YOLOv1 from Scratch

## 📌 Project Overview  
This project is an implementation of **YOLOv1 (You Only Look Once)** from scratch, a real-time object detection model. The implementation includes:  
- **Custom forward pass** with convolutional layers  
- **Loss function** (Bounding Box, Objectness, and Classification loss)  
- **Non-Maximum Suppression (NMS)** for filtering predictions  
- **Training pipeline** with dataset preprocessing  

## 🚀 Features  
✔️ Implemented YOLOv1 architecture from scratch  
✔️ Custom loss function based on the original YOLO paper  
✔️ Training pipeline for object detection  
✔️ Non-Maximum Suppression for post-processing  

## 📂 Project Structure  
- `dataset.py` - Handles data loading and preprocessing  
- `loss.py` - Defines the YOLOv1 loss function  
- `model.py` - Implements the YOLOv1 architecture  
- `train.py` - Training script for the model  
- `utils.py` - Helper functions for post-processing and evaluation  

## 📂 Dataset  
⚠ **Note:** The dataset used for training was **not uploaded** due to its large size. However, you can use datasets like:  
- **Pascal VOC** - [Download here](http://host.robots.ox.ac.uk/pascal/VOC/)  
- **COCO Dataset** - [Download here](https://cocodataset.org/#download)  

## 🛠 Installation & Setup  
1. **Clone the repository:**  
   ```sh
   git clone https://github.com/your-username/yolo-v1-from-scratch.git
   cd yolo-v1-from-scratch
