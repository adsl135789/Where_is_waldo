import os
import cv2
import random

# 調整亮度與對比度
def adjust_brightness_contrast(image, brightness=0, contrast=0):
    # brightness (-255 to 255): 負值降低亮度，正值提高亮度
    # contrast (-127 to 127): 負值降低對比度，正值提高對比度
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)
        image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)

    return image

# 保存調整後的圖片與標籤
def augment_brightness_contrast(input_image_folder, input_label_folder, output_image_folder, output_label_folder, brightness_range=(-50, 50), contrast_range=(-30, 30)):
    # 創建輸出資料夾
    os.makedirs(output_image_folder, exist_ok=True)
    os.makedirs(output_label_folder, exist_ok=True)

    # 遍歷所有圖片
    for image_file in os.listdir(input_image_folder):
        if image_file.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(input_image_folder, image_file)
            label_file = os.path.join(input_label_folder, os.path.splitext(image_file)[0] + ".txt")

            # 確認標籤文件存在
            if not os.path.exists(label_file):
                print(f"標籤文件不存在：{label_file}")
                continue

            # 讀取圖片
            image = cv2.imread(image_path)
            if image is None:
                print(f"無法讀取圖片：{image_path}")
                continue

            # 隨機調整亮度與對比度
            brightness = random.randint(*brightness_range)
            contrast = random.randint(*contrast_range)
            augmented_image = adjust_brightness_contrast(image, brightness=brightness, contrast=contrast)

            # 保存調整後的圖片
            output_image_path = os.path.join(output_image_folder, f"aug_{image_file}")
            cv2.imwrite(output_image_path, augmented_image)

            # 保存對應的標籤
            output_label_path = os.path.join(output_label_folder, f"aug_{os.path.splitext(image_file)[0]}.txt")
            with open(label_file, "r") as infile, open(output_label_path, "w") as outfile:
                for line in infile:
                    outfile.write(line)  # 標籤文件不需改動，直接複製
            print(f"保存調整後圖片與標籤：{output_image_path}, {output_label_path}")

# 使用範例
# input_image_folder = "./augmented_images/"  # 原始圖片資料夾
# input_label_folder = "./augmented_labels/"  # 原始標籤資料夾
input_image_folder = "./data/images/"  # 原始圖片資料夾
input_label_folder = "./data/labels/"  # 原始標籤資料夾
output_image_folder = "augmented_images"  # 調整後圖片的輸出資料夾
output_label_folder = "augmented_labels"  # 調整後標籤的輸出資料夾

augment_brightness_contrast(input_image_folder, input_label_folder, output_image_folder, output_label_folder)
