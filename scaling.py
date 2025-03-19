import os
import random
from PIL import Image
import shutil

def resize_image_and_labels(image_path, label_path, output_image_path, output_label_path, min_scale, max_scale):
    # 打開圖片並獲取原始大小
    image = Image.open(image_path)
    original_width, original_height = image.size

    # 隨機選擇縮放因子
    scale_factor = random.uniform(min_scale, max_scale)
    
    # 計算新的尺寸
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    # 將圖片縮放並保存
    resized_image = image.resize((new_width, new_height))
    resized_image.save(output_image_path)

    # 複製標籤文件到新的路徑（標籤不變）
    shutil.copy(label_path, output_label_path)

def resize_dataset(input_image_folder, input_label_folder, output_image_folder, output_label_folder, min_scale, max_scale):
    # 遍歷所有圖片
    image_files = os.listdir(input_image_folder)

    for image_name in image_files:
        if image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            # 圖片路徑
            image_path = os.path.join(input_image_folder, image_name)
            label_name = image_name.split(".")[0] + ".txt"
            label_path = os.path.join(input_label_folder, label_name)

            # 設定輸出路徑
            output_image_path = os.path.join(output_image_folder, "resize_" + image_name)
            output_label_path = os.path.join(output_label_folder, "resize_" + label_name)

            # 調用函數進行縮放和標籤更新
            resize_image_and_labels(image_path, label_path, output_image_path, output_label_path, min_scale, max_scale)

# 設定資料夾路徑和縮放範圍
input_image_folder = "./metadata/images/"  # 原始圖片資料夾
input_label_folder = "./metadata/labels/"  # 原始標籤資料夾
output_image_folder = "augmented_images"  # 調整後圖片的輸出資料夾
output_label_folder = "augmented_labels"  # 調整後標籤的輸出資料夾
min_scale = 0.8  # 最小縮放比例
max_scale = 1.2  # 最大縮放比例

# 創建輸出資料夾
os.makedirs(output_image_folder, exist_ok=True)
os.makedirs(output_label_folder, exist_ok=True)

# 開始處理資料集
resize_dataset(input_image_folder, input_label_folder, output_image_folder, output_label_folder, min_scale, max_scale)
