from PIL import Image
import random
import os
import math

def rotate_image_and_labels(image_path, label_path, output_image_path, output_label_path, max_angle=3):
    # 開啟圖片
    image = Image.open(image_path)
    width, height = image.size

    # 隨機選擇旋轉角度
    angle = random.uniform(-max_angle, max_angle)

    # 旋轉圖片並保存
    rotated_image = image.rotate(angle, expand=True)
    image_name = os.path.basename(image_path)
    rotated_image_name = f"rotated_{image_name}"
    rotated_image_path = os.path.join(output_image_path, rotated_image_name)
    rotated_image.save(rotated_image_path)

    # 讀取標籤文件
    with open(label_path, "r") as file:
        labels = file.readlines()

    # 更新標籤座標
    new_labels = []
    cx_offset = (rotated_image.size[0] - width) / 2
    cy_offset = (rotated_image.size[1] - height) / 2

    for label in labels:
        class_id, cx, cy, w, h = map(float, label.strip().split())
        cx_abs = cx * width
        cy_abs = cy * height
        w_abs = w * width
        h_abs = h * height

        # 計算旋轉後的新中心點
        cx_rotated, cy_rotated = rotate_point(cx_abs, cy_abs, width / 2, height / 2, math.radians(angle))
        cx_rotated += cx_offset
        cy_rotated += cy_offset

        # 將絕對座標轉回相對座標
        new_cx = cx_rotated / rotated_image.size[0]
        new_cy = cy_rotated / rotated_image.size[1]
        new_w = w_abs / rotated_image.size[0]
        new_h = h_abs / rotated_image.size[1]

        # 限制座標範圍在 [0, 1] 內
        if 0 <= new_cx <= 1 and 0 <= new_cy <= 1:
            new_labels.append(f"{class_id} {new_cx:.6f} {new_cy:.6f} {new_w:.6f} {new_h:.6f}\n")

    # 保存新的標籤文件
    label_name = os.path.basename(label_path)
    rotated_label_name = f"rotated_{label_name}"
    rotated_label_path = os.path.join(output_label_path, rotated_label_name)
    with open(rotated_label_path, "w") as file:
        file.writelines(new_labels)

    print(f"Rotated image saved at {rotated_image_path}")
    print(f"Updated label saved at {rotated_label_path}")
    return rotated_image_path, rotated_label_path


def rotate_point(x, y, cx, cy, angle):
    """
    計算點 (x, y) 圍繞中心點 (cx, cy) 旋轉 angle 後的新座標。
    """
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x -= cx
    y -= cy
    x_new = x * cos_a - y * sin_a + cx
    y_new = x * sin_a + y * cos_a + cy
    return x_new, y_new

def process_folder(input_image_folder, input_label_folder, output_image_folder, output_label_folder, max_angle=3):
    # 確保輸出資料夾存在
    os.makedirs(output_image_folder, exist_ok=True)
    os.makedirs(output_label_folder, exist_ok=True)

    # 遍歷資料夾內所有圖片
    for image_file in os.listdir(input_image_folder):
        if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(input_image_folder, image_file)
            label_path = os.path.join(input_label_folder, os.path.splitext(image_file)[0] + ".txt")
            if os.path.exists(label_path):  # 確保標籤文件存在
                rotate_image_and_labels(image_path, label_path, output_image_folder, output_label_folder, max_angle)


# 範例使用
input_image_folder = "./metadata/images/"
input_label_folder = "./metadata/labels/"
output_image_folder = "augmented_images"
output_label_folder = "augmented_labels"

process_folder(input_image_folder, input_label_folder, output_image_folder, output_label_folder, max_angle=3)