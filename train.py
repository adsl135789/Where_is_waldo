from ultralytics import YOLO


def load_and_train():
    # Load a model
    model = YOLO("yolov8n.yaml")  # build a new model from YAML
    model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)
    model = (
        YOLO("yolov8n.yaml").load("yolov8n.pt")
    )  # build from YAML and transfer weights

    # Train the model
    results = model.train(
        data="./data.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        device="cuda",
        save_period=5,
    )
    model.save("models/yolov8n-trained-100_epochs.pt")


def main():
    print("started")
    load_and_train()


main()
