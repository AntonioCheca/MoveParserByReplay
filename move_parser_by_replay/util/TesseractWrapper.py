import pytesseract
import cv2
import re
from typing import List
from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.util.OpenCVWrapper import OpenCVWrapper


class TesseractWrapper:
    @staticmethod
    def search_numbers_in_image(image: Frame, scale_factor: float = 5.0) -> List[int]:
        # Get the original image data
        img = image.get_image_data()

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Calculate new dimensions
        height, width = gray.shape
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Resize the image (magnify)
        magnified = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        adaptive_thresh = cv2.adaptiveThreshold(magnified, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 11, 2)
        alpha = 2.0  # Contrast control
        beta = 0  # Brightness control
        adjusted = cv2.convertScaleAbs(adaptive_thresh, alpha=alpha, beta=beta)
        denoised = cv2.GaussianBlur(adjusted, (5, 5), 0)

        # Use Tesseract to extract text
        text = pytesseract.image_to_string(denoised, lang='eng',
                                           config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')

        text = text.replace('g', '9')
        # Find all numbers in the extracted text
        OpenCVWrapper.show_image(magnified)
        numbers = re.findall(r'\d+', text)

        return [int(num) for num in numbers]
