import cv2
import argparse


class ColorSelector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.frame = None
        self.selected_colors = []
        self.window_name = "Color Selector"

    def select_frame(self, time_seconds=50):
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
        """Handle mouse events for color selection"""
        if self.frame is not None:
            # Create a copy of the frame to draw on temporarily
            temp_img = self.frame.copy()

            # Display coordinates and color under cursor
            color = self.frame[y, x]
            b, g, r = int(color[0]), int(color[1]), int(color[2])

            # Display color information
            cv2.putText(temp_img, f"Position: X: {x}, Y: {y}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(temp_img, f"Color (BGR): ({b}, {g}, {r})", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Draw markers for all selected colors
            for i, (cx, cy, c_color) in enumerate(self.selected_colors):
                # Draw a circle at the selected point
                cv2.circle(temp_img, (cx, cy), 5, (0, 255, 255), -1)
                # Draw text with color information
                text_pos_y = cy - 20 if cy > 30 else cy + 20
                cv2.putText(temp_img, f"#{i + 1}: ({c_color[0]}, {c_color[1]}, {c_color[2]})",
                            (cx + 10, text_pos_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            # Left mouse button pressed - select color
            if event == cv2.EVENT_LBUTTONDOWN:
                # Get color at clicked position
                color = self.frame[y, x]
                color_tuple = (int(color[0]), int(color[1]), int(color[2]))

                # Save the selected color
                self.selected_colors.append((x, y, color_tuple))

                # Print information
                print(f"Selected Color at Position ({x}, {y}): BGR = {color_tuple}")

                # Draw a circle at the selected point
                cv2.circle(temp_img, (x, y), 5, (0, 255, 255), -1)

            # Display the image with all elements
            cv2.imshow(self.window_name, temp_img)

    def run(self, time_seconds=50):
        """Main method to run the color selector"""
        self.current_time = time_seconds
        if not self.select_frame(self.current_time):
            return

        # Create window and set mouse callback
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # Video properties
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_duration = total_frames / fps
        cap.release()

        # Frame navigation step (in seconds)
        small_step = 1 / fps  # One frame
        medium_step = 0.5  # Half a second
        large_step = 2.0  # Two seconds

        print("\nInstructions:")
        print("- Click on a pixel to select its color")
        print("- Press 'r' to reset all selections")
        print("- Press 'c' to clear the last selection")
        print("- Press 's' to show a summary of all selected colors")
        print("- Navigation:")
        print(f"  * Right arrow: forward {medium_step:.2f} seconds")
        print(f"  * Left arrow: backward {medium_step:.2f} seconds")
        print(f"  * Up arrow: forward {large_step:.1f} seconds")
        print(f"  * Down arrow: backward {large_step:.1f} seconds")
        print(f"  * 'f': forward one frame ({small_step:.4f} seconds)")
        print(f"  * 'd': backward one frame ({small_step:.4f} seconds)")
        print("- Press 'q' or ESC to quit")

        while True:
            # Display the frame with any current selections
            if self.frame is not None:
                display_img = self.frame.copy()

                # Display current time
                cv2.putText(display_img, f"Time: {self.current_time:.2f}s",
                            (10, display_img.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Draw markers for all selected colors
                for i, (x, y, color) in enumerate(self.selected_colors):
                    # Draw a circle at the selected point
                    cv2.circle(display_img, (x, y), 5, (0, 255, 255), -1)
                    # Draw text with color information
                    text_pos_y = y - 20 if y > 30 else y + 20
                    cv2.putText(display_img, f"#{i + 1}: BGR={color}",
                                (x + 10, text_pos_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                cv2.imshow(self.window_name, display_img)

            # Wait for key press
            key = cv2.waitKey(1) & 0xFF

            # Quit on ESC or 'q'
            if key == 27 or key == ord('q'):
                break

            # Reset all selections with 'r'
            elif key == ord('r'):
                self.selected_colors = []
                print("All color selections cleared")

            # Clear last selection with 'c'
            elif key == ord('c') and self.selected_colors:
                self.selected_colors.pop()
                print("Last color selection cleared")

            # Show summary with 's'
            elif key == ord('s'):
                print("\nSelected Colors Summary:")
                for i, (x, y, color) in enumerate(self.selected_colors):
                    print(f"{i + 1}. Position: ({x}, {y}), Color (BGR): {color}")

                if self.selected_colors:
                    print("\nColor Constants for FrameMeterObserver class:")
                    for i, (_, _, color) in enumerate(self.selected_colors):
                        color_name = f"COLOR_{i + 1}"
                        print(f"{color_name} = {color}  # Selected color {i + 1}")

            # Navigation controls
            # Right arrow: forward medium step
            elif key == 83 or key == ord('l'):  # Right arrow
                new_time = min(self.current_time + medium_step, total_duration)
                if new_time != self.current_time:
                    self.current_time = new_time
                    self.select_frame(self.current_time)
                    print(f"Moving to {self.current_time:.2f}s")

            # Left arrow: backward medium step
            elif key == 81 or key == ord('j'):  # Left arrow
                new_time = max(self.current_time - medium_step, 0)
                if new_time != self.current_time:
                    self.current_time = new_time
                    self.select_frame(self.current_time)
                    print(f"Moving to {self.current_time:.2f}s")

            # Up arrow: forward large step
            elif key == 82 or key == ord('i'):  # Up arrow
                new_time = min(self.current_time + large_step, total_duration)
                if new_time != self.current_time:
                    self.current_time = new_time
                    self.select_frame(self.current_time)
                    print(f"Moving to {self.current_time:.2f}s")

            # Down arrow: backward large step
            elif key == 84 or key == ord('k'):  # Down arrow
                new_time = max(self.current_time - large_step, 0)
                if new_time != self.current_time:
                    self.current_time = new_time
                    self.select_frame(self.current_time)
                    print(f"Moving to {self.current_time:.2f}s")

            # 'f': forward one frame
            elif key == ord('f'):
                new_time = min(self.current_time + small_step, total_duration)
                if new_time != self.current_time:
                    self.current_time = new_time
                    self.select_frame(self.current_time)
                    print(f"Moving to frame at {self.current_time:.4f}s")

            # 'd': backward one frame
            elif key == ord('d'):
                new_time = max(self.current_time - small_step, 0)
                if new_time != self.current_time:
                    self.current_time = new_time
                    self.select_frame(self.current_time)
                    print(f"Moving to frame at {self.current_time:.4f}s")

        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Select colors from a video frame")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--time", type=float, default=50.0, help="Time in seconds to extract frame (default: 2.0)")

    args = parser.parse_args()

    selector = ColorSelector(args.video_path)
    selector.run(args.time)


if __name__ == "__main__":
    main()
