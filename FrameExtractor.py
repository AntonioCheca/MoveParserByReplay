import cv2
import numpy as np
import os
import pytesseract
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional, Set
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SF6FrameExtractor')


class Direction(Enum):
    """Enum representing possible directional inputs"""
    NEUTRAL = auto()
    UP = auto()
    DOWN = auto()
    FORWARD = auto()
    BACK = auto()
    UP_FORWARD = auto()
    UP_BACK = auto()
    DOWN_FORWARD = auto()
    DOWN_BACK = auto()


class Button(Enum):
    """Enum representing possible button inputs"""
    LP = auto()  # Light Punch (Blue)
    MP = auto()  # Medium Punch (Yellow)
    HP = auto()  # Heavy Punch (Red)
    LK = auto()  # Light Kick (Blue)
    MK = auto()  # Medium Kick (Yellow)
    HK = auto()  # Heavy Kick (Red)


@dataclass
class InputState:
    """Represents the state of a player's input at a given frame"""
    direction: Direction
    buttons: Set[Button]
    frame_count: int  # How many frames this input has been active


@dataclass
class FrameInputs:
    """Represents inputs from both players at a specific frame"""
    frame_number: int
    p1_inputs: InputState
    p2_inputs: InputState


class InputDisplay:
    """Class responsible for detecting and parsing the input display"""

    def __init__(self, p1_region: Tuple[int, int, int, int], p2_region: Tuple[int, int, int, int]):
        """
        Initialize with the screen regions for player inputs

        Args:
            p1_region: Tuple of (x, y, width, height) for Player 1's input display
            p2_region: Tuple of (x, y, width, height) for Player 2's input display
        """
        self.p1_region = p1_region
        self.p2_region = p2_region

    def extract_input_regions(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Extract input display regions for both players from the frame"""
        p1_x, p1_y, p1_w, p1_h = self.p1_region
        p2_x, p2_y, p2_w, p2_h = self.p2_region

        p1_display = frame[p1_y:p1_y + p1_h, p1_x:p1_x + p1_w]
        p2_display = frame[p2_y:p2_y + p2_h, p2_x:p2_x + p2_w]

        return p1_display, p2_display

    def preprocess_for_ocr(self, region: np.ndarray) -> np.ndarray:
        """Preprocess the input region for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to make text more visible
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Optional: Apply additional preprocessing if needed
        # thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

        return thresh

    def parse_frame_count(self, region: np.ndarray) -> Optional[List[int]]:
        """
        Extract the frame counts from an input display region

        Returns:
            List of frame counts visible in the display, or None if detection failed
        """
        processed = self.preprocess_for_ocr(region)

        # Use pytesseract to extract text
        text = pytesseract.image_to_string(processed, config='--psm 6 -c tessedit_char_whitelist=0123456789')

        # Extract numbers using regex
        numbers = re.findall(r'\d+', text)

        if not numbers:
            return None

        # Convert to integers
        try:
            return [int(num) for num in numbers]
        except ValueError:
            return None

    def has_frame_advanced(self, prev_counts: List[int], current_counts: List[int]) -> bool:
        """
        Determine if the game frame has advanced by comparing input display frames

        Args:
            prev_counts: Previous frame's input display numbers
            current_counts: Current frame's input display numbers

        Returns:
            True if the game frame has advanced, False otherwise
        """
        # If counts are different lengths, frame has likely advanced
        if len(prev_counts) != len(current_counts):
            return True

        # Check if any count has changed
        for i in range(min(len(prev_counts), len(current_counts))):
            # If the number increased by 1 or reset from 99 to 1
            if (current_counts[i] == prev_counts[i] + 1) or (prev_counts[i] == 99 and current_counts[i] == 1):
                return True

        return False


import cv2
import numpy as np
import os
import pytesseract
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional, Set
import logging
import re

# Character life data
SF6_CHARACTER_MAX_LIFE = {
    "Ryu": 10000,
    "Ken": 10000,
    "Chun-Li": 10000,
    "Guile": 10000,
    "Zangief": 11000,
    "Dhalsim": 10000,
    "E. Honda": 10000,
    "Blanka": 10000,
    "Dee Jay": 10000,
    "Cammy": 10000,
    "Lily": 10000,
    "Jamie": 10000,
    "Luke": 10000,
    "Kimberly": 10000,
    "Juri": 10000,
    "Marisa": 10000,
    "Manon": 10000,
    "JP": 10000,
    "Rashid": 10000,
    "A.K.I.": 10000,
    "Ed": 10000,
    "Akuma": 9000,
    "Mai": 10000,
    "Terry": 10000,
    "M. Bison": 10000,
    "Unknown": 10000
}


class DamageTracker:
    """Class for tracking damage in the combo display"""

    def __init__(self, p1_damage_region: Tuple[int, int, int, int], p2_damage_region: Tuple[int, int, int, int]):
        """
        Initialize with the screen regions for combo damage displays

        Args:
            p1_damage_region: Tuple of (x, y, width, height) for Player 1's damage display
            p2_damage_region: Tuple of (x, y, width, height) for Player 2's damage display
        """
        self.p1_damage_region = p1_damage_region
        self.p2_damage_region = p2_damage_region

        # Track damage history
        self.p1_damage_history = []
        self.p2_damage_history = []

        # Track current life
        self.p1_current_life = 10000  # Will be adjusted based on character
        self.p2_current_life = 10000  # Will be adjusted based on character

        # Track combos (start when damage > 0, end when damage returns to 0)
        self.p1_in_combo = False
        self.p2_in_combo = False

        # Track total damage for current round
        self.p1_total_damage_taken = 0
        self.p2_total_damage_taken = 0

    def extract_damage_regions(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Extract combo damage display regions for both players from the frame"""
        p1_x, p1_y, p1_w, p1_h = self.p1_damage_region
        p2_x, p2_y, p2_w, p2_h = self.p2_damage_region

        p1_display = frame[p1_y:p1_y + p1_h, p1_x:p1_x + p1_w]
        p2_display = frame[p2_y:p2_y + p2_h, p2_x:p2_x + p2_w]

        return p1_display, p2_display

    def preprocess_for_ocr(self, region: np.ndarray) -> np.ndarray:
        """Preprocess the damage region for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

        # Increase contrast
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

        # Optional: Apply additional preprocessing for damage numbers
        # thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

        return thresh

    def extract_damage(self, region: np.ndarray) -> int:
        """Extract the damage value from a combo display region"""
        processed = self.preprocess_for_ocr(region)

        # Use pytesseract to extract text - specific config for numbers
        text = pytesseract.image_to_string(
            processed,
            config='--psm 7 -c tessedit_char_whitelist=0123456789'
        )

        # Extract numbers using regex
        numbers = re.findall(r'\d+', text)

        if not numbers:
            return 0

        # Return the largest number (in case of multiple detections)
        try:
            return max(int(num) for num in numbers)
        except ValueError:
            return 0

    def update(self, frame: np.ndarray) -> Tuple[bool, bool]:
        """
        Process a new frame and update damage tracking

        Returns:
            Tuple of (p1_ko_detected, p2_ko_detected) booleans
        """
        p1_region, p2_region = self.extract_damage_regions(frame)

        p1_current_damage = self.extract_damage(p1_region)
        p2_current_damage = self.extract_damage(p2_region)

        # Add to history
        self.p1_damage_history.append(p1_current_damage)
        self.p2_damage_history.append(p2_current_damage)

        # Keep history manageable
        if len(self.p1_damage_history) > 120:  # About 2 seconds at 60fps
            self.p1_damage_history.pop(0)
            self.p2_damage_history.pop(0)

        # Check for combo start/end for P1
        if p1_current_damage > 0 and not self.p1_in_combo:
            self.p1_in_combo = True
        elif p1_current_damage == 0 and self.p1_in_combo:
            # Combo ended - get max damage from recent history
            if len(self.p1_damage_history) >= 2:
                max_combo_damage = max(self.p1_damage_history[:-1])  # Exclude current 0
                self.p2_total_damage_taken += max_combo_damage
                self.p2_current_life -= max_combo_damage
            self.p1_in_combo = False

        # Check for combo start/end for P2
        if p2_current_damage > 0 and not self.p2_in_combo:
            self.p2_in_combo = True
        elif p2_current_damage == 0 and self.p2_in_combo:
            # Combo ended - get max damage from recent history
            if len(self.p2_damage_history) >= 2:
                max_combo_damage = max(self.p2_damage_history[:-1])  # Exclude current 0
                self.p1_total_damage_taken += max_combo_damage
                self.p1_current_life -= max_combo_damage
            self.p2_in_combo = False

        # Check for KO situations
        p1_ko_detected = self.p1_current_life <= 0
        p2_ko_detected = self.p2_current_life <= 0

        return p1_ko_detected, p2_ko_detected

    def reset_for_new_round(self):
        """Reset damage tracking for a new round"""
        self.p1_damage_history = []
        self.p2_damage_history = []
        self.p1_in_combo = False
        self.p2_in_combo = False
        self.p1_total_damage_taken = 0
        self.p2_total_damage_taken = 0
        # Life will be reset by CharacterDetector when it calls set_character_life

    def set_character_life(self, p1_character: str, p2_character: str):
        """Update starting life based on characters"""
        self.p1_current_life = SF6_CHARACTER_MAX_LIFE.get(p1_character, 10000)
        self.p2_current_life = SF6_CHARACTER_MAX_LIFE.get(p2_character, 10000)


class LifeBarTracker:
    """Class for tracking the life bars at the top of the screen"""

    def __init__(self, p1_lifebar_region: Tuple[int, int, int, int], p2_lifebar_region: Tuple[int, int, int, int]):
        """
        Initialize with the screen regions for life bars

        Args:
            p1_lifebar_region: Tuple of (x, y, width, height) for Player 1's life bar
            p2_lifebar_region: Tuple of (x, y, width, height) for Player 2's life bar
        """
        self.p1_lifebar_region = p1_lifebar_region
        self.p2_lifebar_region = p2_lifebar_region

        # Track life percentage history
        self.p1_life_history = []
        self.p2_life_history = []

        # Life percentages (0-100)
        self.p1_life_percent = 100
        self.p2_life_percent = 100

    def extract_lifebar_regions(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Extract life bar regions for both players from the frame"""
        p1_x, p1_y, p1_w, p1_h = self.p1_lifebar_region
        p2_x, p2_y, p2_w, p2_h = self.p2_lifebar_region

        p1_bar = frame[p1_y:p1_y + p1_h, p1_x:p1_x + p1_w]
        p2_bar = frame[p2_y:p2_y + p2_h, p2_x:p2_x + p2_w]

        return p1_bar, p2_bar

    def process_lifebar(self, bar_region: np.ndarray) -> float:
        """
        Process a life bar region to determine life percentage

        Returns:
            Life percentage (0-100)
        """
        # Convert to HSV to better detect the life bar color
        hsv = cv2.cvtColor(bar_region, cv2.COLOR_BGR2HSV)

        # SF6 life bars are typically yellow-green
        # Adjust these ranges based on actual color in your videos
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])

        # Create mask for life bar color
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Count non-zero pixels (life bar)
        life_pixels = cv2.countNonZero(mask)

        # Calculate percentage based on filled portion
        total_pixels = bar_region.shape[0] * bar_region.shape[1]
        if total_pixels > 0:
            life_percent = (life_pixels / total_pixels) * 100
        else:
            life_percent = 0

        return life_percent

    def update(self, frame: np.ndarray) -> Tuple[bool, bool]:
        """
        Process a new frame and update life bar tracking

        Returns:
            Tuple of (p1_ko_detected, p2_ko_detected) booleans
        """
        p1_bar, p2_bar = self.extract_lifebar_regions(frame)

        self.p1_life_percent = self.process_lifebar(p1_bar)
        self.p2_life_percent = self.process_lifebar(p2_bar)

        # Add to history
        self.p1_life_history.append(self.p1_life_percent)
        self.p2_life_history.append(self.p2_life_percent)

        # Keep history manageable
        if len(self.p1_life_history) > 60:  # About 1 second at 60fps
            self.p1_life_history.pop(0)
            self.p2_life_history.pop(0)

        # Check for KO situations (life near 0%)
        p1_ko_detected = self.p1_life_percent < 5  # Using threshold of 5%
        p2_ko_detected = self.p2_life_percent < 5

        return p1_ko_detected, p2_ko_detected

    def reset_for_new_round(self):
        """Reset life bar tracking for a new round"""
        self.p1_life_history = []
        self.p2_life_history = []
        self.p1_life_percent = 100
        self.p2_life_percent = 100


class CharacterDetector:
    """Class for detecting the characters being used"""

    def __init__(self, p1_name_region: Tuple[int, int, int, int], p2_name_region: Tuple[int, int, int, int]):
        """
        Initialize with the screen regions for character names

        Args:
            p1_name_region: Tuple of (x, y, width, height) for Player 1's character name
            p2_name_region: Tuple of (x, y, width, height) for Player 2's character name
        """
        self.p1_name_region = p1_name_region
        self.p2_name_region = p2_name_region

        # Store detected characters
        self.p1_character = "Unknown"
        self.p2_character = "Unknown"

        # List of possible character names for matching
        self.character_names = list(SF6_CHARACTER_MAX_LIFE.keys())

    def extract_name_regions(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Extract character name regions for both players from the frame"""
        p1_x, p1_y, p1_w, p1_h = self.p1_name_region
        p2_x, p2_y, p2_w, p2_h = self.p2_name_region

        p1_name = frame[p1_y:p1_y + p1_h, p1_x:p1_x + p1_w]
        p2_name = frame[p2_y:p2_y + p2_h, p2_x:p2_x + p2_w]

        return p1_name, p2_name

    def preprocess_for_ocr(self, region: np.ndarray) -> np.ndarray:
        """Preprocess the name region for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

        # Enhance contrast
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Scale up for better OCR
        scaled = cv2.resize(thresh, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        return scaled

    def match_character_name(self, detected_text: str) -> str:
        """
        Match the detected text to a known character name

        Returns:
            Matched character name or "Unknown"
        """
        # Remove non-alphabetic characters and whitespace
        cleaned_text = re.sub(r'[^a-zA-Z\s\.-]', '', detected_text).strip()

        # Try to find the closest match
        best_match = "Unknown"
        best_score = 0

        for character in self.character_names:
            # Simple matching - can be improved with fuzzy matching
            if character.lower() in cleaned_text.lower():
                if len(character) > best_score:
                    best_match = character
                    best_score = len(character)

        return best_match

    def update(self, frame: np.ndarray) -> Tuple[str, str]:
        """
        Process a new frame and update character detection

        Returns:
            Tuple of (p1_character, p2_character) strings
        """
        p1_region, p2_region = self.extract_name_regions(frame)

        p1_processed = self.preprocess_for_ocr(p1_region)
        p2_processed = self.preprocess_for_ocr(p2_region)

        # Use pytesseract to extract text
        p1_text = pytesseract.image_to_string(p1_processed)
        p2_text = pytesseract.image_to_string(p2_processed)

        # Match to known characters
        p1_detected = self.match_character_name(p1_text)
        p2_detected = self.match_character_name(p2_text)

        # Only update if we have a valid detection
        if p1_detected != "Unknown":
            self.p1_character = p1_detected

        if p2_detected != "Unknown":
            self.p2_character = p2_detected

        return self.p1_character, self.p2_character


class RoundIndicatorTracker:
    """Class for tracking the round indicators at the top of the screen"""

    def __init__(self, p1_rounds_region: Tuple[int, int, int, int], p2_rounds_region: Tuple[int, int, int, int]):
        """
        Initialize with the screen regions for round indicators

        Args:
            p1_rounds_region: Tuple of (x, y, width, height) for Player 1's round indicators
            p2_rounds_region: Tuple of (x, y, width, height) for Player 2's round indicators
        """
        self.p1_rounds_region = p1_rounds_region
        self.p2_rounds_region = p2_rounds_region

        # Track round wins
        self.p1_rounds_won = 0
        self.p2_rounds_won = 0

        # Previous state to detect changes
        self.prev_p1_rounds = 0
        self.prev_p2_rounds = 0

    def extract_rounds_regions(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Extract round indicator regions for both players from the frame"""
        p1_x, p1_y, p1_w, p1_h = self.p1_rounds_region
        p2_x, p2_y, p2_w, p2_h = self.p2_rounds_region

        p1_rounds = frame[p1_y:p1_y + p1_h, p1_x:p1_x + p1_w]
        p2_rounds = frame[p2_y:p2_y + p2_h, p2_x:p2_x + p2_w]

        return p1_rounds, p2_rounds

    def count_round_indicators(self, region: np.ndarray) -> int:
        """
        Count the number of round indicators that show as 'won'
        Uses color detection to identify wins vs empty indicators

        Returns:
            Number of rounds won
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

        # SF6 round win indicators are typically yellow/gold or have letters
        # We'll look for bright pixels vs dark/empty indicators
        _, thresh = cv2.threshold(cv2.cvtColor(region, cv2.COLOR_BGR2GRAY), 150, 255, cv2.THRESH_BINARY)

        # Count non-zero (bright) pixels
        bright_pixels = cv2.countNonZero(thresh)

        # Calculate the percentage of bright pixels
        total_pixels = region.shape[0] * region.shape[1]
        if total_pixels == 0:
            return 0

        bright_percentage = (bright_pixels / total_pixels) * 100

        # If brightness exceeds threshold, count as a round win
        # Fine-tune this threshold based on your actual footage
        if bright_percentage > 25:  # Adjust as needed
            return 1
        else:
            return 0

    def detect_round_wins(self, p1_region: np.ndarray, p2_region: np.ndarray) -> Tuple[int, int]:
        """
        Detect round wins from indicators

        Returns:
            Tuple of (p1_rounds, p2_rounds)
        """
        # For actual implementation, you might want to split the region
        # into individual indicators and analyze each

        # Simplified approach: count total "bright" spots in the round indicators
        p1_rounds = self.count_round_indicators(p1_region)
        p2_rounds = self.count_round_indicators(p2_region)

        return p1_rounds, p2_rounds

    def update(self, frame: np.ndarray) -> bool:
        """
        Process a new frame and update round tracking

        Returns:
            True if a new round victory was detected, False otherwise
        """
        p1_region, p2_region = self.extract_rounds_regions(frame)

        p1_rounds, p2_rounds = self.detect_round_wins(p1_region, p2_region)

        # Check for round changes
        round_change_detected = False

        if p1_rounds > self.prev_p1_rounds:
            self.p1_rounds_won = p1_rounds
            round_change_detected = True

        if p2_rounds > self.prev_p2_rounds:
            self.p2_rounds_won = p2_rounds
            round_change_detected = True

        # Update previous state
        self.prev_p1_rounds = p1_rounds
        self.prev_p2_rounds = p2_rounds

        return round_change_detected

    def reset_for_new_match(self):
        """Reset round tracking for a new match"""
        self.p1_rounds_won = 0
        self.p2_rounds_won = 0
        self.prev_p1_rounds = 0
        self.prev_p2_rounds = 0


class RoundState(Enum):
    """Enum for tracking the current state of a round"""
    UNKNOWN = auto()
    PRE_ROUND = auto()
    IN_PROGRESS = auto()
    ROUND_ENDING = auto()
    ROUND_ENDED = auto()
    MATCH_ENDED = auto()


class EnhancedRoundDetector:
    """Enhanced class for detecting round transitions in SF6 replays"""

    def __init__(self,
                 input_display: InputDisplay,
                 damage_tracker: DamageTracker,
                 lifebar_tracker: LifeBarTracker,
                 character_detector: CharacterDetector,
                 round_tracker: RoundIndicatorTracker):
        """
        Initialize with all the tracking components

        Args:
            input_display: InputDisplay instance for tracking input frame advances
            damage_tracker: DamageTracker instance for tracking combo damage
            lifebar_tracker: LifeBarTracker instance for tracking life bars
            character_detector: CharacterDetector instance for character detection
            round_tracker: RoundIndicatorTracker instance for round indicators
        """
        self.input_display = input_display
        self.damage_tracker = damage_tracker
        self.lifebar_tracker = lifebar_tracker
        self.character_detector = character_detector
        self.round_tracker = round_tracker

        # State tracking
        self.current_state = RoundState.UNKNOWN
        self.inactive_frames = 0
        self.rounds_completed = 0

        # Input display tracking
        self.previous_frame_counts = None
        self.frames_without_input_change = 0

        # Logger
        self.logger = logging.getLogger("RoundDetector")

    def update(self, frame: np.ndarray) -> Tuple[RoundState, bool]:
        """
        Process a new frame and update round state

        Args:
            frame: The current video frame

        Returns:
            Tuple of (current_state, new_round_detected)
        """
        # Update all trackers
        p1_character, p2_character = self.character_detector.update(frame)
        self.damage_tracker.set_character_life(p1_character, p2_character)

        p1_damage_ko, p2_damage_ko = self.damage_tracker.update(frame)
        p1_lifebar_ko, p2_lifebar_ko = self.lifebar_tracker.update(frame)
        round_indicator_changed = self.round_tracker.update(frame)

        # Extract input display regions
        p1_input, p2_input = self.input_display.extract_input_regions(frame)

        # Parse frame counts
        p1_counts = self.input_display.parse_frame_count(p1_input)
        p2_counts = self.input_display.parse_frame_count(p2_input)

        # Combine counts for easier processing
        current_counts = []
        if p1_counts:
            current_counts.extend(p1_counts)
        if p2_counts:
            current_counts.extend(p2_counts)

        # Check if input display has advanced
        input_advanced = False
        if self.previous_frame_counts is not None and current_counts:
            input_advanced = self.input_display.has_frame_advanced(self.previous_frame_counts, current_counts)

            if not input_advanced:
                self.frames_without_input_change += 1
            else:
                self.frames_without_input_change = 0

        self.previous_frame_counts = current_counts if current_counts else self.previous_frame_counts

        # Determine KO condition - using multiple indicators
        ko_detected = (p1_damage_ko or p2_damage_ko or p1_lifebar_ko or p2_lifebar_ko)

        # Update state machine
        new_round_detected = False
        previous_state = self.current_state

        if self.current_state == RoundState.UNKNOWN:
            # Initial state, try to determine where we are
            if current_counts and len(current_counts) > 0:
                self.current_state = RoundState.IN_PROGRESS

        elif self.current_state == RoundState.IN_PROGRESS:
            # Check for round ending conditions
            if ko_detected:
                self.current_state = RoundState.ROUND_ENDING
                self.logger.info("KO detected - round ending")

            # Another way to detect round ending - input display stops updating
            elif self.frames_without_input_change > 120:  # 2 seconds without input updates
                self.current_state = RoundState.ROUND_ENDING
                self.logger.info("Input display inactive - possible round ending")

        elif self.current_state == RoundState.ROUND_ENDING:
            # Waiting for confirmation through round indicators
            if round_indicator_changed:
                self.current_state = RoundState.ROUND_ENDED
                self.logger.info("Round indicator changed - round confirmed ended")

            # Or just wait for a significant pause in the input display
            elif self.frames_without_input_change > 180:  # 3 seconds without input updates
                self.current_state = RoundState.ROUND_ENDED
                self.logger.info("Extended input inactivity - round assumed ended")

        elif self.current_state == RoundState.ROUND_ENDED:
            # Check if we're starting a new round
            if input_advanced and self.frames_without_input_change < 10:
                self.current_state = RoundState.IN_PROGRESS
                self.rounds_completed += 1
                new_round_detected = True

                # Reset trackers for new round
                self.damage_tracker.reset_for_new_round()
                self.lifebar_tracker.reset_for_new_round()

                self.logger.info(f"New round detected - round {self.rounds_completed}")

            # Check if match has ended (typically after 2 rounds for one player)
            elif self.round_tracker.p1_rounds_won >= 2 or self.round_tracker.p2_rounds_won >= 2:
                self.current_state = RoundState.MATCH_ENDED
                self.logger.info("Match ended")

        # Log state changes
        if previous_state != self.current_state:
            self.logger.debug(f"State changed: {previous_state} -> {self.current_state}")

        return self.current_state, new_round_detected

    def reset(self):
        """Reset the detector for a new match"""
        self.current_state = RoundState.UNKNOWN
        self.inactive_frames = 0
        self.rounds_completed = 0
        self.previous_frame_counts = None
        self.frames_without_input_change = 0

        # Reset all trackers
        self.damage_tracker.reset_for_new_round()
        self.lifebar_tracker.reset_for_new_round()
        self.round_tracker.reset_for_new_match()


class FrameExtractor:
    """Main class for extracting unique game frames from video"""

    def __init__(self, input_display: InputDisplay, round_detector: EnhancedRoundDetector,
                 output_dir: str = "extracted_frames"):
        """
        Initialize the frame extractor

        Args:
            input_display: InputDisplay instance for processing input displays
            round_detector: RoundDetector instance for detecting round start/end
            output_dir: Directory to save extracted frames
        """
        self.input_display = input_display
        self.round_detector = round_detector
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def process_video(self, video_path: str) -> List[str]:
        """
        Process a video file to extract unique game frames

        Args:
            video_path: Path to the input video file

        Returns:
            List of paths to the generated round videos
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Error: Could not open video {video_path}")
            return []

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Variables for tracking
        round_number = 0
        frame_number = 0
        round_frame_number = 0
        current_round_frames = []
        prev_p1_counts = None
        prev_p2_counts = None
        round_videos = []

        logger.info(f"Processing video: {video_path}")
        logger.info(f"Video properties: {width}x{height}, {fps} fps")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_number += 1

            # Detect round state
            round_state = self.round_detector.detect_state(frame)

            # If we're in a round, process the frame
            if round_state == RoundState.IN_ROUND:
                # Extract input displays
                p1_region, p2_region = self.input_display.extract_input_regions(frame)

                # Parse frame counts
                p1_counts = self.input_display.parse_frame_count(p1_region)
                p2_counts = self.input_display.parse_frame_count(p2_region)

                # Skip frames where we couldn't detect counts
                if p1_counts is None and p2_counts is None:
                    logger.warning(f"Frame {frame_number}: Could not detect any input display counts")
                    continue

                # Check if the game frame has advanced
                frame_advanced = False

                if prev_p1_counts is not None and p1_counts is not None:
                    frame_advanced = frame_advanced or self.input_display.has_frame_advanced(prev_p1_counts, p1_counts)

                if prev_p2_counts is not None and p2_counts is not None:
                    frame_advanced = frame_advanced or self.input_display.has_frame_advanced(prev_p2_counts, p2_counts)

                # If frame has advanced, save it
                if frame_advanced or (prev_p1_counts is None and prev_p2_counts is None):
                    current_round_frames.append(frame.copy())
                    round_frame_number += 1

                    # Save individual frame for debugging/analysis
                    frame_path = os.path.join(self.output_dir,
                                              f"round_{round_number}_frame_{round_frame_number:04d}.png")
                    cv2.imwrite(frame_path, frame)

                    logger.debug(f"Frame {frame_number}: Game frame advanced, saved as {frame_path}")

                # Update previous counts
                prev_p1_counts = p1_counts
                prev_p2_counts = p2_counts

            # If round ended, save the round video
            elif round_state == RoundState.ROUND_ENDED and current_round_frames:
                round_number += 1

                # Create video for this round
                round_video_path = os.path.join(self.output_dir, f"round_{round_number}.mp4")
                self._create_round_video(current_round_frames, round_video_path, fps)
                round_videos.append(round_video_path)

                # Reset for next round
                current_round_frames = []
                round_frame_number = 0
                prev_p1_counts = None
                prev_p2_counts = None

                logger.info(f"Round {round_number} completed: {len(current_round_frames)} frames")

        # Handle the case where the video ends during a round
        if round_state == RoundState.IN_ROUND and current_round_frames:
            round_number += 1
            round_video_path = os.path.join(self.output_dir, f"round_{round_number}.mp4")
            self._create_round_video(current_round_frames, round_video_path, fps)
            round_videos.append(round_video_path)

            logger.info(f"Final round {round_number} completed: {len(current_round_frames)} frames")

        cap.release()
        logger.info(f"Video processing complete: {len(round_videos)} rounds extracted")

        return round_videos

    def _create_round_video(self, frames: List[np.ndarray], output_path: str, fps: float):
        """Create a video file from a list of frames"""
        if not frames:
            logger.warning(f"No frames to write for {output_path}")
            return

        height, width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for frame in frames:
            out.write(frame)

        out.release()
        logger.info(f"Created round video: {output_path}")


def main():
    """Main function to run the frame extractor"""
    # Define input display regions (adjust these based on your video)
    width = 1920
    height = 1080
    margin = 42
    input_display_width = 290
    input_display_height = 143
    input_display_altitude = 225
    p1_region = (margin, input_display_altitude, input_display_width, input_display_height)
    p2_region = (
    width - input_display_width - margin, input_display_altitude, input_display_width, input_display_height)

    # Initialize components
    input_display = InputDisplay(p1_region, p2_region)
    round_detector = EnhancedRoundDetector()
    extractor = FrameExtractor(input_display, round_detector, "output")

    # Process video
    video_path = "data/match1.mkv"
    round_videos = extractor.process_video(video_path)

    print(f"Extracted {len(round_videos)} round videos:")
    for video in round_videos:
        print(f"  - {video}")


if __name__ == "__main__":
    main()
