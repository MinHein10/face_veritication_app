import cv2
import numpy as np
from deepface import DeepFace
import config
from logger import logger

def enhance_for_documents(img):
    """
    Powerful enhancement for low-quality scans/IDs.
    Uses CLAHE + Sharpening.
    """
    # 1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # This brings out details in grainy or flat scans
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # 2. Sharpening (Unsharp Mask)
    gaussian_blur = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
    final = cv2.addWeighted(enhanced, 1.6, gaussian_blur, -0.6, 0)
    return final

def check_image_quality(img_path, is_source=True):
    """
    Analyzes an image for quality, focusing on the center region.
    Attempts to auto-sharpen if slightly blurry.
    Returns (is_ok, message, quality_info)
    is_source: True if it's the ID/NRC, False if it's the Live Selfie.
    """
    try:
        img = cv2.imread(img_path)
        if img is None:
            return False, "Could not read image file. Please re-upload.", {}

        # Set threshold based on image type
        threshold = config.BLUR_THRESHOLD_SOURCE if is_source else config.BLUR_THRESHOLD_TARGET

        def get_scores(target_img):
            gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            roi_y1, roi_y2 = int(h * 0.2), int(h * 0.8)
            roi_x1, roi_x2 = int(w * 0.2), int(w * 0.8)
            face_zone = gray[roi_y1:roi_y2, roi_x1:roi_x2]
            l_var = cv2.Laplacian(face_zone, cv2.CV_64F).var()
            bright = np.mean(face_zone)
            return l_var, bright

        laplacian_var, avg_brightness = get_scores(img)
        
        # --- AUTO-ENHANCE FOR DOCUMENTS ---
        if laplacian_var < threshold:
            logger.info(f"Quality low ({laplacian_var:.2f}). Applying PRO-Enhancement...")
            enhanced_img = enhance_for_documents(img)
            new_var, new_bright = get_scores(enhanced_img)
            
            # Save the enhanced version
            cv2.imwrite(img_path, enhanced_img)
            laplacian_var, avg_brightness = new_var, new_bright
        
        quality_info = {
            "blur_score": round(laplacian_var, 2),
            "brightness_score": round(avg_brightness, 2),
            "type": "Source/ID" if is_source else "Target/Live"
        }
        
        if laplacian_var < threshold:
            return False, f"Photo is too blurry ({laplacian_var:.1f}). Requirements: {threshold}", quality_info

        if avg_brightness < config.BRIGHTNESS_RANGE[0]:
            return False, "Photo is too dark.", quality_info

        if avg_brightness > config.BRIGHTNESS_RANGE[1]:
            return False, "Photo is too bright.", quality_info

        return True, "Quality OK", quality_info
    except Exception as e:
        logger.error(f"Quality check error: {str(e)}")
        return False, "Unexpected error during quality check.", {}

def verify_faces(img1_path, img2_path):
    """
    Verifies if faces in two images belong to the same person.
    img1: Source/ID, img2: Live Target
    """
    logger.info(f"Starting verification: {img1_path} vs {img2_path}")

    # Perform Quality Assessment (Split logic)
    ok1, msg1, q1 = check_image_quality(img1_path, is_source=True)
    ok2, msg2, q2 = check_image_quality(img2_path, is_source=False)

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



