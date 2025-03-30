import cv2
import argparse


class RegionSelector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.frame = None
        self.drawing = False
        self.start_point = (-1, -1)
        self.end_point = (-1, -1)
        self.rectangles = []
        self.current_rect = None
        self.window_name = "Region Selector"

    def select_frame(self, time_seconds=2):
        """Extract a frame at the specified time"""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {self.video_path}")
            return False

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps

        print(f"Video duration: {duration:.2f} seconds")
        print(f"FPS: {fps}")

        # Check if requested time is valid
        if time_seconds > duration:
            print(f"Warning: Requested time {time_seconds}s exceeds video duration. Using last frame.")
            time_seconds = duration

        # Set frame position
        frame_pos = int(fps * time_seconds)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)

        # Read the frame
        ret, self.frame = cap.read()
        cap.release()

        if not ret:
            print("Error: Could not read frame")
            return False

        print(f"Frame extracted at {time_seconds} seconds")
        return True

    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drawing rectangles"""
        # Display current mouse position
        if self.frame is not None:
            # Create a copy of the frame to draw on temporarily
            temp_img = self.frame.copy()

            # Draw all saved rectangles
            for rect in self.rectangles:
                cv2.rectangle(temp_img, rect[0], rect[1], (0, 255, 0), 2)

            # Display coordinates
            cv2.putText(temp_img, f"X: {x}, Y: {y}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Left mouse button pressed - start drawing rectangle
            if event == cv2.EVENT_LBUTTONDOWN:
                self.drawing = True
                self.start_point = (x, y)

            # Mouse moving while button is pressed - update rectangle
            elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
                self.end_point = (x, y)
                # Draw current rectangle
                cv2.rectangle(temp_img, self.start_point, self.end_point, (0, 0, 255), 2)

            # Left mouse button released - finish drawing rectangle
            elif event == cv2.EVENT_LBUTTONUP:
                self.drawing = False
                self.end_point = (x, y)

                # Calculate the correct coordinates
                x1, y1 = min(self.start_point[0], self.end_point[0]), min(self.start_point[1], self.end_point[1])
                x2, y2 = max(self.start_point[0], self.end_point[0]), max(self.start_point[1], self.end_point[1])
                width, height = x2 - x1, y2 - y1

                # Save rectangle
                self.rectangles.append(((x1, y1), (x2, y2)))

                # Print information
                print(f"Selected Region: (x={x1}, y={y1}, width={width}, height={height})")
                print(f"Tuple format: ({x1}, {y1}, {width}, {height})")

            # Display the image with all elements
            cv2.imshow(self.window_name, temp_img)

    def run(self):
        """Main method to run the region selector"""
        if not self.select_frame():
            return

        # Create window and set mouse callback
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        print("\nInstructions:")
        print("- Click and drag to select a region")
        print("- Press 'r' to reset all selections")
        print("- Press 'c' to clear the last selection")
        print("- Press 'q' or ESC to quit")

        while True:
            # Display the frame with any current drawings
            if self.frame is not None:
                display_img = self.frame.copy()

                # Draw all saved rectangles
                for i, rect in enumerate(self.rectangles):
                    cv2.rectangle(display_img, rect[0], rect[1], (0, 255, 0), 2)
                    # Display region number
                    cv2.putText(display_img, f"Region {i + 1}",
                                (rect[0][0], rect[0][1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                cv2.imshow(self.window_name, display_img)

            # Wait for key press
            key = cv2.waitKey(1) & 0xFF

            # Quit on ESC or 'q'
            if key == 27 or key == ord('q'):
                break

            # Reset all selections with 'r'
            elif key == ord('r'):
                self.rectangles = []
                print("All selections cleared")

            # Clear last selection with 'c'
            elif key == ord('c') and self.rectangles:
                self.rectangles.pop()
                print("Last selection cleared")

        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Select regions from a video frame")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--time", type=float, default=2.0, help="Time in seconds to extract frame (default: 2.0)")

    args = parser.parse_args()

    selector = RegionSelector(args.video_path)
    selector.select_frame(args.time)
    selector.run()


if __name__ == "__main__":
    main()