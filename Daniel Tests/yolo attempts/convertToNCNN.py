from ultralytics import YOLO

# Load a YOLO26n PyTorch model
model = YOLO("yolo26n-seg.pt")

# Export the model to NCNN format
model.export(format="ncnn")  # creates 'yolo26n_ncnn_model'