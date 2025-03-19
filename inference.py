from ultralytics import YOLO
from PIL import Image, ImageDraw
import os
from customLib import *


# Load a pretrained model
model_name = "final"
model = YOLO(f"models/{model_name}.pt")

input_files = list_image_files("tests/input")
print(input_files)

for file in input_files[0]:
    # the width and height of the windows that will be cropped from the main image
    window_width, window_height = (640, 640)
    # the current image that is loaded from the list and to be processed
    main_image = Image.open(file)
    # get original image width and height
    image_width, image_height = main_image.width, main_image.height
    # calculate x and y stride
    stride_x, stride_y = (int(window_width / 2), int(window_height / 2))

    #
    # get number of windows on x and y axis's
    #
    # number of horizontal windows
    windows_x = int((image_width) / stride_x)
    # number of vertical windows
    windows_y = int((image_height) / stride_y)
    # * loop trough vertical windows:
    bounding_boxes = []
    box_found = False
    for window_y in range(windows_y):
        total_stride_y = window_y * stride_y
        for window_x in range(windows_x):
            total_stride_x = window_x * stride_x
            section_image = crop_image(
                main_image,
                xy=(total_stride_x, total_stride_y),
                wh=(window_width, window_height),
            )
            outputs = model.predict(
                save=False,
                source=section_image,
                show_labels=False,
                show_boxes=True,
                conf=0.01,
            )
            for out in outputs:
                if out.boxes.shape[0] == 0 or box_found == True:
                    continue
                prediction = out.boxes.xywhn[0]  # extract the
                prediction = prediction.tolist()  # convert to list
                prediction.insert(0, 1)  # prefix with the label 0
                box = get_box_coordonates(
                    section_xy=(total_stride_x, total_stride_y),
                    section_wh=(section_image.width, section_image.height),
                    box_xywhn=prediction,
                )
                bounding_boxes.append(box)
                box_found = True
    for box in bounding_boxes:
        draw = None
        image_for_label = main_image.copy()

        image = draw_rectangle(
            image=image_for_label, label_contents=box, return_image=True
        )
        file_name = os.path.basename(file)
        image.save(f"./tests/output/final/{file_name}")
