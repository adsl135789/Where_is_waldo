import numpy as np
import cv2
import random
import os

def random_erasing(image, area_ratio=0.02, min_aspect_ratio=0.3, max_attempts=50):
    """
    隨機遮擋增強（Random Erasing）函數。
    
    :param image: 輸入的圖片，為 NumPy 陣列（H, W, C）。
    :param area_ratio: 遮擋區域面積占整體圖片面積的比例。
    :param min_aspect_ratio: 遮擋區域的最小寬高比。
    :param max_attempts: 隨機選擇遮擋區域的最大嘗試次數。
    :return: 增強後的圖片。
    """
    height, width, _ = image.shape
    target_area = height * width * area_ratio

    for _ in range(max_attempts):
        # 隨機選擇遮擋區域的寬度和高度
        aspect_ratio = random.uniform(min_aspect_ratio, 1 / min_aspect_ratio)
        h = int(np.sqrt(target_area * aspect_ratio))
        w = int(np.sqrt(target_area / aspect_ratio))

        if w <= width and h <= height:
            # 隨機選擇遮擋區域的左上角位置
            x1 = random.randint(0, width - w)
            y1 = random.randint(0, height - h)

            # 隨機生成遮擋區域的顏色（這裡選擇填充為白色）
            image[y1:y1 + h, x1:x1 + w] = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
            return image, (x1, y1, w, h)

    # 如果超過最大嘗試次數仍然無法找到合適區域，則返回原圖
    return image, None

def update_labels(label_file, x1, y1, w, h, image_width, image_height):
    """
    更新標籤檔案中的物體位置，確保它們仍然正確反映在增強後的圖片上。
    
    :param label_file: 標籤檔案路徑。
    :param x1, y1, w, h: 遮擋區域的位置和大小。
    :param image_width, image_height: 圖片的寬度和高度。
    :return: 更新後的標籤內容。
    """
    with open(label_file, 'r') as f:
        labels = f.readlines()

    updated_labels = []
    for label in labels:
        label_data = label.strip().split()
        class_id = int(label_data[0])
        x_center = float(label_data[1]) * image_width
        y_center = float(label_data[2]) * image_height
        width = float(label_data[3]) * image_width
        height = float(label_data[4]) * image_height

        # 檢查物體是否在遮擋區域內，若是則移除該物體
        if x_center > x1 + w or x_center < x1 or y_center > y1 + h or y_center < y1:
            # 更新物體標註為相對比例格式
            updated_labels.append(f"{class_id} {x_center / image_width} {y_center / image_height} {width / image_width} {height / image_height}\n")

    return updated_labels

def apply_augmentation_to_dataset(image_dir, label_dir, output_image_dir, output_label_dir, area_ratio=0.02):
    """
    遍歷資料集中的所有圖片和標籤，進行遮擋增強並保存增強後的圖片和標籤。
    
    :param image_dir: 圖片資料夾路徑。
    :param label_dir: 標籤資料夾路徑。
    :param output_image_dir: 輸出圖片資料夾路徑。
    :param output_label_dir: 輸出標籤資料夾路徑。
    :param area_ratio: 遮擋區域面積占整體圖片面積的比例。
    """
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
    if not os.path.exists(output_label_dir):
        os.makedirs(output_label_dir)

    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg') or f.endswith('.png')]

    for image_file in image_files:
        image_path = os.path.join(image_dir, image_file)
        label_file = os.path.join(label_dir, os.path.splitext(image_file)[0] + '.txt')
        
        # 讀取圖片
        image = cv2.imread(image_path)
        height, width, _ = image.shape

        # 隨機遮擋增強
        augmented_image, mask = random_erasing(image.copy(), area_ratio)
        
        if mask:
            # 更新標籤
            updated_labels = update_labels(label_file, *mask, width, height)

            # 保存增強後的圖片
            output_image_path = os.path.join(output_image_dir, f"eras_{image_file}")
            cv2.imwrite(output_image_path, augmented_image)

            # 保存更新後的標籤
            output_label_path = os.path.join(output_label_dir, f"eras_{os.path.splitext(image_file)[0]}.txt")
            with open(output_label_path, 'w') as f:
                f.writelines(updated_labels)

if __name__ == "__main__":
    # 設定資料夾路徑
    image_dir = './metadata/images/'
    label_dir = './metadata/labels/'
    output_image_dir = 'augmented_images'
    output_label_dir = 'augmented_labels'
    # 執行遮擋增強並保存增強後的圖片和標籤
    apply_augmentation_to_dataset(image_dir, label_dir, output_image_dir, output_label_dir)
