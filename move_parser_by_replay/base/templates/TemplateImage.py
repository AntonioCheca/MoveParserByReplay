import cv2
import os

import numpy as np


class TemplateImage:
    name: str
    image: np.ndarray

    def __init__(self, path_file: str):
        file_name = os.path.basename(path_file)
        self.name = os.path.splitext(file_name)[0]
        open_cv_image = cv2.imread(path_file, cv2.IMREAD_UNCHANGED)
        changed_image_to_video_format = cv2.cvtColor(open_cv_image, cv2.COLOR_BGRA2BGR)
        scaled_image = cv2.resize(changed_image_to_video_format, None, fx=1.1, fy=1.1, interpolation=cv2.INTER_LINEAR)
        self.image = np.asarray(scaled_image)

    def get_name(self) -> str:
        return self.name

    def get_image(self) -> np.ndarray:
        return self.image

    def __repr__(self):
        return self.name
