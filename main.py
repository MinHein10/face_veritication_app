import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import tkinter as tk
from ui import FaceVerifierApp
from logger import logger

def main():
    """
    Main entry point for the Face Verification System.
    """
    logger.info("Application starting...")
    try:
        root = tk.Tk()
        app = FaceVerifierApp(root)
        root.mainloop()
        logger.info("Application closed normally.")
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)

if __name__ == "__main__":
    main()