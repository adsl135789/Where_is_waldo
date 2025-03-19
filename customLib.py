import os
from PIL import Image, ImageDraw
import pandas as pd


def list_image_files(folder_path):
    all_files = os.listdir(folder_path)
    # filter out jpg and png files
    img_files = [
        file for file in all_files if file.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    # get files full path
    img_files = [os.path.join(folder_path, file) for file in img_files]
    return img_files


def get_box_coordonates(section_xy, section_wh, box_xywhn=None):
    section_width, section_height = section_wh
    section_x, section_y = section_xy
    # opened image size

    label_data = box_xywhn
    label_norm_x: int = label_data[1]  # box center x coordonate (NORMALISED)
    label_norm_y: int = label_data[2]  # box center y coordonate (NORMALISED)
    label_norm_box_width = label_data[3]  # box width (NORMALISED)
    label_norm_box_height = label_data[4]  # box height (NORMALISED)

    # box coordonates
    x0: int = int(label_norm_x * section_width)
    y0: int = int(label_norm_y * section_height)
    label_width: int = int(label_norm_box_width * section_width)
    label_height: int = int(label_norm_box_height * section_height)
    box = (
        int(section_x + (x0 - int(label_width / 2))),
        int(section_y + (y0 - int(label_height / 2))),
        int(section_x + (x0 + int(label_width / 2))),
        int(section_y + (y0 + int(label_height / 2))),
    )

    # breakpoint()

    return box


def load_label(label_path):
    df = pd.read_csv(filepath_or_buffer=label_path, header=None, sep=" ")
    return df.iloc[0]


def crop_image(image, xy=(50, 50), wh=(640, 640)):
    x, y = xy
    right, bottom = tuple(a + b for a, b in zip(wh, xy))
    image = image.crop((x, y, right, bottom))
    return image


# image path - 'relative or absolute path to the image we are loading
# size - Tuple (width, height) - the size of the box
def draw_rectangle(
    image_path=None, image=None, label_path=None, label_contents=None, return_image=True
):
    if image_path != None:
        image = Image.open(image_path)
        img_name, _ = os.path.splitext(os.path.basename(image_path))

    # opened image size
    img_width = image.width
    img_height = image.height
    label_data = ""
    box = None  # initialising box tuple
    if label_path != None:
        label_path = (
            label_path
            if label_path is not None
            else f"./datasets/train/labels/{img_name}.txt"
        )
        label_data = load_label(label_path)

        label_norm_x = label_data[1]
        label_norm_y = label_data[2]
        label_norm_box_width = label_data[3]
        label_norm_box_height = label_data[4]
        # box coordonates
        x0: int = int(label_norm_x * img_width)
        y0: int = int(label_norm_y * img_height)
        x1: int = int(label_norm_box_width * img_width)
        y1: int = int(label_norm_box_height * img_height)

        box = ((x0 - x1 / 2, y0 - y1 / 2), (x0 + x1 / 2, y0 + y1 / 2))
    if label_contents != None:
        box = label_contents

    # load label data
    draw = ImageDraw.Draw(image)

    # draw.rectangle(box, outline="red", width=10)
    draw.rectangle(box, outline="yellow", width=3)
    if return_image == True:
        return image
    else:
        image.show()


def create_files(image_content, label_content, image_path, label_path):
    # saving the image
    image_content.save(image_path)
    # saving the label
    with open(label_path) as file:
        file.write(label_content)


def get_labelIn_window(
    section_xy, section_wh, orig_label_xy, orig_label_wh, label_number=0
):
    # destructure parameter data from tuples into variables
    section_x, section_y = section_xy
    section_w, section_h = section_wh
    orig_label_x, orig_label_y = orig_label_xy
    orig_label_w, orig_label_h = orig_label_wh

    # get new label xy coordonates based on window position and original label position
    new_label_x = (orig_label_x - (orig_label_w / 2)) - section_x
    new_label_y = (orig_label_y - (orig_label_h / 2)) - section_y

    # set new label coordonates (normalised)
    norm_new_label_x = round(new_label_x / section_w, 6)
    norm_new_label_y = round(new_label_y / section_h, 6)
    norm_orig_label_w = round(orig_label_w / section_w, 6)
    norm_orig_label_h = round(orig_label_h / section_h, 6)
    label_coordonates = f"{label_number} {norm_new_label_x} {norm_new_label_y} {norm_orig_label_w} {norm_orig_label_h}"
    # see if label is fully visible in width and height and is not cut off
    is_visible_label = (
        ((orig_label_w / 2) + new_label_x)
        <= section_w  # 70% of the label is inside the width box
        and ((orig_label_h / 2) + new_label_y)
        <= section_h  # 70% of the label is inside the height box
        and norm_new_label_x >= 0
        and norm_new_label_y >= 0
        and norm_orig_label_w >= 0
        and norm_orig_label_h >= 0
    )
    # return label coordonates if the label is fully visible and empty string if not
    return label_coordonates if is_visible_label else ""


def generate_windows(input_folder, dest_path, window_wh=(640, 640), stride_percent=0.5):
    # load all images in a folder
    files = os.listdir(input_folder + "/images")
    window_width, window_height = window_wh
    stride = int(window_width * stride_percent)
    image_files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    count = 0
    # cycle trough images
    for image_name in image_files:
        # image object
        image = Image.open(f"{input_folder}/images/{image_name}")
        [img_name, img_extension] = image_name.split(".")
        image_width, image_height = image.size

        w_windows = int(image_width / stride)  # nr of strides in image width
        h_windows = int(image_height / stride)  # nr of strides in image height
        count = 0  # incrementing to name the files uniquely
        for y in range(h_windows):

            is_last_y_window = False
            # detecting the last y iteration
            if y + 1 == h_windows:
                # setting a variable to know it is the last iteration
                is_last_y_window = True
                # y position window logic
            new_slice_y = (
                image_height - window_height  # last window to the right
                if is_last_y_window == True  # if it's the last itaration
                else y * stride  # normal stride calculation for y
            )
            # cycling trough sections in height
            for x in range(w_windows):
                #
                # if this is the last horizontal window w_section iteration
                #
                is_last_x_window = False
                if x + 1 == w_windows:
                    is_last_x_window = True
                    # breakpoint()
                new_slice_x = (
                    int(image_width - window_width)
                    if is_last_x_window == True
                    else x * stride
                )
                # crop window to be
                new_slice_xy = (new_slice_x, new_slice_y)
                new_slice_wh = (window_width, window_height)
                section_image = crop_image(
                    image,
                    xy=new_slice_xy,
                    wh=new_slice_wh,
                )

                # save image file in output folder with _count appended postfix name
                image_dest_file = (
                    f"{dest_path}images/{img_name}_{count}.{img_extension}"
                )
                # if is_last_x_window:
                #     print(image_dest_file)
                # save label destination path
                label_dest_file = f"{dest_path}/labels/{img_name}_{count}.txt"
                # test image with bounding box generationg (to be commented out when actually using)
                section_image.save(image_dest_file)
                # read current image label
                # Open the file in read mode
                with open(f"{input_folder}/labels/{img_name}.txt", "r") as file:
                    # Read all lines into a list
                    lines = file.readlines()

                # Strip newline characters from each line (optional)
                labels = [line.strip() for line in lines]
                # cycle trough labels
                index = 0
                final_label_text = ""
                for label_data_string in labels:
                    label_data_list = label_data_string.split(" ")
                    label_wh = (
                        (float(label_data_list[3]) * image_width),
                        (float(label_data_list[4]) * image_height),
                    )
                    label_w, label_h = label_wh
                    label_xy = (
                        (float(label_data_list[1]) * image_width) + (label_w / 2),
                        (float(label_data_list[2]) * image_height) + (label_h / 2),
                    )

                    # get the label that's possibly inside this window
                    label_in_window = get_labelIn_window(
                        section_xy=(new_slice_x, new_slice_y),
                        section_wh=window_wh,
                        orig_label_xy=label_xy,
                        orig_label_wh=label_wh,
                        label_number=index,
                    )

                    if len(label_in_window) > 0:
                        final_label_text += label_in_window + "\n"
                    else:
                        final_label_text = label_in_window

                # save the label for the image:
                with open(label_dest_file, "w") as file:
                    file.write(final_label_text)
                count += 1
