import cv2
import numpy as np
import easyocr
from pytesseract import pytesseract

from move_parser_by_replay.base.Frame import Frame
from move_parser_by_replay.base.Region import Region
from move_parser_by_replay.observers.input_display.InputDisplayObserver import InputDisplayTemplateObserver
from move_parser_by_replay.util.NumberInReplayWrapper import NumberInReplayWrapper


class TextDetectionService:
    def __init__(self, video_path: str, frame_position: int, region: tuple):
        """
        Initializes the service with the video path, frame position, and region of interest.

        :param video_path: The path to the video file
        :param frame_position: The specific frame number to process
        :param region: The region of interest in the form (x, y, width, height)
        """
        self.video_path = video_path
        self.frame_position = frame_position
        self.region = region

        # Initialize EasyOCR reader
        self.reader = easyocr.Reader(['en'])

    def get_frame(self):
        """
        Extracts a specific frame from the video.

        :return: The image at the specific frame position
        """
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_position)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise ValueError(f"Could not read frame {self.frame_position} from the video.")

        # Crop the frame based on the given region
        x, y, w, h = self.region
        frame = frame[y:y + h, x:x + w]

        return frame

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image by enhancing contrast, applying thresholding, and morphological operations.

        :param image: The input image
        :return: The processed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_image = clahe.apply(gray)

        # Apply binary thresholding to isolate white text (invert the text)
        _, binary_image = cv2.threshold(enhanced_image, 75, 255, cv2.THRESH_BINARY_INV)

        # Apply morphological operations (dilation followed by erosion) to refine text edges
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(binary_image, kernel, iterations=1)
        eroded_image = cv2.erode(dilated_image, kernel, iterations=1)

        return eroded_image

    def find_text_using_easyocr(self, image: np.ndarray) -> list:
        """
        Uses EasyOCR to detect text in the image.

        :param image: The preprocessed input image
        :return: List of detected text coordinates and values
        """
        result = self.reader.readtext(image, detail=1, allowlist='0123456789')
        matches = [(item[0], item[1]) for item in result]  # (coordinates, text)
        return matches

    def process(self):
        """
        Main function to process the video frame and detect text.

        :return: List of detected text in the frame
        """
        # Step 1: Extract the specified frame from the video
        frame = self.get_frame()

        # Step 3: Find text using EasyOCR
        text_matches = self.find_text_using_easyocr(frame)

        return text_matches

    def show_image(self, image: np.ndarray) -> None:
        """
        Displays the image for visual inspection.

        :param image: Image to be displayed
        """
        cv2.imshow("Processed Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


# Example of how to use the service

video_path = "./data/match1.mkv"

for i in range(50):
    frame_position = 650 + i
    region = (50, 227, 35, 34)  # Example region of interest
    input_display = InputDisplayTemplateObserver(1, Region(*region))

    # Create the service instance
    service = TextDetectionService(video_path, frame_position, region)
    import time

    start = time.time()
    # Process the frame and get detected text
    text_matches = NumberInReplayWrapper.search_numbers_in_image(Frame(service.get_frame()),
                                                                 input_display.get_numbers())
    end = time.time()
    print(end - start)

    # Show the matches (if any)
    print(f"Found {len(text_matches)} text matches: {text_matches}")

    # Optional: Display the processed image for debugging
    frame = service.get_frame()
    service.show_image(frame)
