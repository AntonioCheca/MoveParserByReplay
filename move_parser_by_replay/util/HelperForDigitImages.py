import cv2
import numpy as np
import os
from pathlib import Path


def process_digit_image(input_path, output_path=None):
    # Read the image
    img = cv2.imread(input_path)

    # Convert to grayscale for processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to separate foreground from background
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find bounding box around the digit
    if contours:
        x_min, y_min = img.shape[1], img.shape[0]
        x_max, y_max = 0, 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)

        # Add a small padding around the digit
        padding = 2
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(img.shape[1], x_max + padding)
        y_max = min(img.shape[0], y_max + padding)

        # Crop the image to the bounding box
        cropped = img[y_min:y_max, x_min:x_max]

        # Determine output path if not provided
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"processed_{input_file.name}")

        # Save the result
        cv2.imwrite(output_path, cropped)
        return output_path

    return None


# Process a single image
def process_single_image(path):
    result_path = process_digit_image(path)
    print(f"Processed image saved to: {result_path}")


# Process all digit images in a directory
def process_directory(directory):
    for file in os.listdir(directory):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(directory, file)
            result_path = process_digit_image(input_path)
            print(f"Processed {file} -> {result_path}")


# Or uncomment this to process all images in a directory
# process_directory("path/to/your/templates/folder")
# Use this to process a single image
# process_single_image("path/to/your/digit.png")

# Or uncomment this to process all images in a directory
process_directory("./data/numbers/")
