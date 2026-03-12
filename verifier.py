import cv2
import numpy as np
from deepface import DeepFace
import config
from logger import logger

def check_image_quality(img_path):
    """
    Analyzes an image for blurriness and brightness.
    Returns (is_ok, message)
    """
    try:
        img = cv2.imread(img_path)
        if img is None:
            return False, "Could not read image file.", {}


        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Check for Blurriness using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 2. Check for Brightness
        avg_brightness = np.mean(gray)
        
        quality_info = {
            "blur_score": laplacian_var,
            "brightness_score": avg_brightness
        }
        
        if laplacian_var < config.BLUR_THRESHOLD:
            return False, f"Image is too blurry ({laplacian_var:.1f}). Please use a sharper photo.", quality_info
            
        if avg_brightness < config.BRIGHTNESS_RANGE[0]:
            return False, "Image is too dark. Please use better lighting.", quality_info
            
        if avg_brightness > config.BRIGHTNESS_RANGE[1]:
            return False, "Image is too bright (overexposed).", quality_info
            
        return True, "Quality OK", quality_info
    except Exception as e:
        return False, f"Quality check error: {str(e)}", {}

def verify_faces(img1_path, img2_path):
    """
    Verifies if faces in two images belong to the same person using settings from config.
    Now includes quality assessment.
    """
    logger.info(f"Starting verification: {img1_path} vs {img2_path}")
    
    # Perform Quality Assessment
    ok1, msg1, q1 = check_image_quality(img1_path)
    ok2, msg2, q2 = check_image_quality(img2_path)
    
    if not ok1:
        logger.warning(f"Image 1 Quality Failed: {msg1}")
        return {"verified": False, "distance": "N/A", "error": f"Photo 1 Quality: {msg1}"}
    if not ok2:
        logger.warning(f"Image 2 Quality Failed: {msg2}")
        return {"verified": False, "distance": "N/A", "error": f"Photo 2 Quality: {msg2}"}

    try:
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name=config.MODEL_NAME,
            detector_backend=config.DETECTOR_BACKEND,
            distance_metric=config.DISTANCE_METRIC,
            align=config.ALIGN,
            enforce_detection=config.ENFORCE_DETECTION
        )

        logger.info(f"All Result : {result}")
        # Attach quality info to results
        result['quality'] = {'img1': q1, 'img2': q2}
        
        logger.info(f"Verification completed. Result: {result['verified']}, Distance: {result['distance']}")
        return result

    except ValueError as ve:
        logger.warning(f"Face detection failed: {ve}")
        return {"verified": False, "distance": "N/A", "error": f"No face detected: {str(ve)}"}
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}")
        return {"verified": False, "distance": "Error", "error": str(e)}



