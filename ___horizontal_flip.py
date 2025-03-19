import os
import cv2

# 讀取標籤文件，解析 YOLO 格式
def read_yolo_labels(label_file):
    bboxes = []
    with open(label_file, "r") as file:
        lines = file.readlines()
        for line in lines:
            class_id, x_center, y_center, width, height = map(float, line.strip().split())
            bboxes.append([class_id, x_center, y_center, width, height])
    return bboxes

# 保存標籤文件
def save_yolo_labels(label_file, bboxes):
    with open(label_file, "w") as file:
        for bbox in bboxes:
            line = " ".join(map(str, bbox))
            file.write(line + "\n")

# 水平翻轉影像與標籤
def horizontal_flip(image, bboxes):
    h, w, _ = image.shape
    flipped_image = cv2.flip(image, 1)  # 水平翻轉影像
    new_bboxes = []
    for bbox in bboxes:
        class_id, x_center, y_center, width, height = bbox
        x_center_new = 1 - x_center  # 更新中心點的 X 座標
        new_bboxes.append([class_id, x_center_new, y_center, width, height])
    return flipped_image, new_bboxes

# 主函數：處理所有影像與標籤
def augment_and_save(input_image_folder, input_label_folder, output_image_folder, output_label_folder):
    # 創建輸出文件夾
    os.makedirs(output_image_folder, exist_ok=True)
    os.makedirs(output_label_folder, exist_ok=True)

    # 遍歷所有圖片
    for image_file in os.listdir(input_image_folder):
        if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
            # 讀取影像
            image_path = os.path.join(input_image_folder, image_file)
            image = cv2.imread(image_path)

            # 對應的標籤文件
            label_file = os.path.join(input_label_folder, os.path.splitext(image_file)[0] + ".txt")
            if not os.path.exists(label_file):
                print(f"標籤文件不存在：{label_file}")
                continue

            # 讀取標籤
            bboxes = read_yolo_labels(label_file)

            # 應用水平翻轉
            flipped_image, flipped_bboxes = horizontal_flip(image, bboxes)

            # 保存增強後的圖片
            output_image_path = os.path.join(output_image_folder, "flipped_" + image_file)
            cv2.imwrite(output_image_path, flipped_image)

            # 保存更新後的標籤
            output_label_path = os.path.join(output_label_folder, "flipped_" + os.path.splitext(image_file)[0] + ".txt")
            save_yolo_labels(output_label_path, flipped_bboxes)

            print(f"保存增強影像：{output_image_path}")
            print(f"保存增強標籤：{output_label_path}")

# 使用範例
input_image_folder = "./data/images/"  # 原始圖片資料夾
input_label_folder = "./data/labels/"  # 原始標籤資料夾
output_image_folder = "./augmented_images"  # 增強後圖片資料夾
output_label_folder = "./augmented_labels"  # 增強後標籤資料夾

augment_and_save(input_image_folder, input_label_folder, output_image_folder, output_label_folder)
