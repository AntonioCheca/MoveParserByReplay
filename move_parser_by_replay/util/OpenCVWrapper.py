import cv2
import numpy as np


class OpenCVWrapper:
    DEFAULT_THRESHOLD_FOR_TEMPLATE_MATCHING = 0.7
    DEFAULT_MIN_MATCH_COUNT = 1

    @staticmethod
    def search_image_by_template(image: np.ndarray, template: np.ndarray,
                                 threshold: float = DEFAULT_THRESHOLD_FOR_TEMPLATE_MATCHING):
        OpenCVWrapper.validate_types(image, template)
        OpenCVWrapper.validate_same_shape(image, template)
        OpenCVWrapper.validate_image_larger_than_template(image, template)
        OpenCVWrapper.validate_color_channel_consistency(image, template)

        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matches = list(zip(*locations[::-1]))
        return matches

    @staticmethod
    def validate_color_channel_consistency(image, template):
        if len(image.shape) == 3 and len(template.shape) == 3:
            if image.shape[2] != template.shape[2]:
                raise ValueError(f"Image has {image.shape[2]} channels while template has {template.shape[2]} channels")

    @staticmethod
    def validate_types(image, template):
        if not isinstance(image, np.ndarray) or not isinstance(template, np.ndarray):
            raise ValueError("Both image and template must be numpy arrays")

    @staticmethod
    def validate_image_larger_than_template(image, template):
        if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
            raise ValueError("Template cannot be larger than the image")

    @staticmethod
    def validate_same_shape(image, template):
        if len(image.shape) != len(template.shape):
            raise ValueError("Image and template must have the same number of dimensions")

    @staticmethod
    def show_image(image) -> None:
        image_name = "Image"
        cv2.imshow(image_name, image)
        cv2.moveWindow(image_name, 1000, 800)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def search_image_with_scaling(image: np.ndarray, template: np.ndarray,
                                  threshold: float = DEFAULT_THRESHOLD_FOR_TEMPLATE_MATCHING,
                                  min_scale: float = 0.5, max_scale: float = 2.0, num_scales: int = 100):
        OpenCVWrapper.validate_types(image, template)
        OpenCVWrapper.validate_color_channel_consistency(image, template)

        best_matches = []
        scale_factors = np.linspace(min_scale, max_scale, num_scales)

        for scale in scale_factors:
            scaled_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

            if scaled_template.shape[0] > image.shape[0] or scaled_template.shape[1] > image.shape[1]:
                continue  # Skip if the template is larger than the image

            matches = OpenCVWrapper.search_image_by_template(image, scaled_template, threshold)
            if len(matches) > 0:
                best_matches.append([scale, matches[0]])

        return best_matches

    @staticmethod
    def search_image_by_sift(image, template, min_match_count=DEFAULT_MIN_MATCH_COUNT, ratio_thresh=0.7):
        # Validate inputs
        OpenCVWrapper.validate_types(image, template)
        OpenCVWrapper.validate_image_larger_than_template(image, template)
        OpenCVWrapper.validate_color_channel_consistency(image, template)

        # Convert images to grayscale if they're color
        if len(image.shape) == 3:
            img1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            img1 = image.copy()

        if len(template.shape) == 3:
            img2 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            img2 = template.copy()

        # Initialize SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # Find keypoints and descriptors
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        # If no features found in either image, return empty list
        if des1 is None or des2 is None or len(des1) == 0 or len(des2) == 0:
            return []

        # FLANN parameters and matcher initialization
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Find 2 nearest matches for each descriptor
        matches = flann.knnMatch(des2, des1, k=2)

        # Apply Lowe's ratio test to filter good matches
        good_matches = []
        for m, n in matches:
            if m.distance < ratio_thresh * n.distance:
                good_matches.append(m)

        # If not enough good matches, return empty list
        if len(good_matches) < min_match_count:
            return []

        # Extract location of good matches
        src_pts = np.float32([kp2[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp1[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Find homography
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        # Get corners of template
        h, w = img2.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # Transform corners to coordinates in original image
        dst = cv2.perspectiveTransform(pts, M)

        # Calculate center point
        center_x = int(np.mean([p[0][0] for p in dst]))
        center_y = int(np.mean([p[0][1] for p in dst]))

        # Return center point as match location
        return [(center_x, center_y)]
