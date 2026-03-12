# Face Verification System Configuration

# DeepFace Settings
MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"
DISTANCE_METRIC = "cosine"
ALIGN = True
ENFORCE_DETECTION = True

# UI Settings
WINDOW_TITLE = "Pro Face Verifier v1.0"
WINDOW_SIZE = "800x600"
IMAGE_SIZE = (250, 250)

# Face Quality Thresholds
BLUR_THRESHOLD = 50.0       # Higher is sharper. Images below this are considered "Blurry".
BRIGHTNESS_RANGE = (40, 220) # 0-255 scale. Outside this is "Too Dark" or "Too Bright".
MIN_FACE_SIZE = 80          # Minimum width/height of detected face in pixels.

