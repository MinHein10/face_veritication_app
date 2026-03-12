import logging
import os

def setup_logger():
    """
    Sets up a professional logger that outputs to both console and a file.
    """
    logger = logging.getLogger("FaceVerifier")
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    fh = logging.FileHandler("logs/verification.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

logger = setup_logger()
