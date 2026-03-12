from deepface import DeepFace
import config
from logger import logger

def verify_faces(img1_path, img2_path):
    """
    Verifies if faces in two images belong to the same person using settings from config.
    """
    logger.info(f"Starting verification: {img1_path} vs {img2_path}")
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
        logger.info(f"Verification completed. Result: {result['verified']}, Distance: {result['distance']}")
        return result

    except ValueError as ve:
        logger.warning(f"Face detection failed: {ve}")
        return {"verified": False, "distance": "N/A", "error": f"No face detected: {str(ve)}"}
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}")
        return {"verified": False, "distance": "Error", "error": str(e)}


