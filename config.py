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
# SOURCE (ID/NRC): Very low threshold for scans/documents
BLUR_THRESHOLD_SOURCE = 10.0  
# TARGET (Live Photo): Higher threshold to ensure clear selfie
BLUR_THRESHOLD_TARGET = 35.0

BRIGHTNESS_RANGE = (25, 245) 
MIN_FACE_SIZE = 50

