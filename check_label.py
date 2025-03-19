import os
import cv2

# 讀取 YOLO 格式標籤
def read_yolo_labels(label_file):
    bboxes = []
    with open(label_file, "r") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                class_id, x_center, y_center, width, height = map(float, parts)
                bboxes.append([int(class_id), x_center, y_center, width, height])
    return bboxes

# 在圖片上繪製 Bounding Box
def draw_bounding_boxes(image, bboxes, class_names=None):
    h, w, _ = image.shape
    for bbox in bboxes:
        class_id, x_center, y_center, box_width, box_height = bbox

        # 計算 Bounding Box 的左上角與右下角像素座標
        x1 = int((x_center - box_width / 2) * w)
        y1 = int((y_center - box_height / 2) * h)
        x2 = int((x_center + box_width / 2) * w)
        y2 = int((y_center + box_height / 2) * h)

        # 畫矩形框
        color = (0, 0, 0)  
        thickness = 2
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

        # 添加標籤文字
        if class_names:
            label = class_names[class_id]
        else:
            label = str(class_id)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        text_color = (0, 255, 0)
        cv2.putText(image, label, (x1, y1 - 10), font, font_scale, text_color, thickness)

    return image

# 主函數：處理所有圖片與標籤
def visualize_labels(input_image_folder, input_label_folder, output_folder, class_names=None):
    # 創建輸出文件夾
    os.makedirs(output_folder, exist_ok=True)

    # 遍歷所有圖片
    for image_file in os.listdir(input_image_folder):
        if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(input_image_folder, image_file)
            label_file = os.path.join(input_label_folder, os.path.splitext(image_file)[0] + ".txt")

            # 確認標籤文件存在
            if not os.path.exists(label_file):
                print(f"標籤文件不存在：{label_file}")
                continue

            # 讀取圖片與標籤
            image = cv2.imread(image_path)
            if image is None:
                print(f"無法讀取圖片：{image_path}")
                continue

            bboxes = read_yolo_labels(label_file)

            # 在圖片上繪製 Bounding Box
            image_with_boxes = draw_bounding_boxes(image, bboxes, class_names)

            # 保存結果圖片
            output_image_path = os.path.join(output_folder, image_file)
            cv2.imwrite(output_image_path, image_with_boxes)
            print(f"保存繪製結果：{output_image_path}")

# 使用範例
input_image_folder = "./augmented_images/"  # 原始圖片資料夾
input_label_folder = "./augmented_labels/"  # 原始標籤資料夾
# input_image_folder = "./labelled_data/train/images/"  # 原始圖片資料夾
# input_label_folder = "./labelled_data/train/labels/"  # 原始標籤資料夾
output_folder = "visualized_images"  # 繪製後圖片的輸出資料夾
class_names = ["Waldo"]  # 替換為實際的類別名稱（可選）
visualize_labels(input_image_folder, input_label_folder, output_folder, class_names)
