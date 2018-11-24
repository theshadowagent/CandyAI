from time import time, sleep
from color_extractor import predict_color, detect_close_patter, DEFAULT_COLOR_PATTERNS, adjust_gamma
from cut_body import get_body
from datetime import datetime
import os
import cv2



class DetectingManager:
    def __init__(self):
        pass

    def parse_frame(self, frame, detected_entities, delete_tmp_files=False):
        for entity_name, entity_bound in detected_entities.items():
            print(entity_name, entity_bound)

            filename = str(datetime.now()) + ".png"
            with open(filename, 'wb') as f:
                ((x, y), (x2, y2)) = entity_bound
                img_slide = frame[y:y2, x:x2, :]
                adjust_gamma(img_slide, 1.5)
                cv2.imwrite(filename, img_slide)

            if entity_name == "person":
                cutted_image_path = get_body("./" + filename)
                with open(filename, "rb") as f:
                    top_colors = detect_close_patter(None, f, DEFAULT_COLOR_PATTERNS)
                    print(top_colors)
                    color = sorted(top_colors.items(), key=lambda x: x[1])[0][0]
                    print(str(color) + " cloths")

            elif entity_name in ["backpack", "handbag", "bird", "cat", "dog", "horse","sheep", "cow", "elephant", "bear", "zebra", "giraffe", "hat", "umbrella", "eye-glasses", "tie", "suitcase", "bottle", "cup", "banana", "apple", "sandwich", "orange", "cloth", "clothes", "fruit"]:
                with open(filename, "rb") as f:
                    color = predict_color(None, f, 1)
                    print(str(color) + entity_name)

            if delete_tmp_files:
                os.remove(filename)
                if cutted_image_path:
                    os.remove(cutted_image_path)
        # sleep(5)
        # sleep(10)

