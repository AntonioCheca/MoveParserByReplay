import pytesseract
import cv2
from typing import Any
from move_parser_by_replay.base.Frame import Frame


class TesseractWrapper:
    @staticmethod
    def search_text_in_image(image: Frame, scale_factor: float = 5.0) -> Any:
        img = image.get_image_data()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        height, width = gray.shape
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        magnified = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        text = pytesseract.image_to_string(magnified, lang='eng', config='--psm 6 --oem 3')

        return text
