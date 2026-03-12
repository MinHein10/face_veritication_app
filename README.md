# Professional Face Verification System

A high-accuracy face verification application built with Python, DeepFace, and Tkinter. This system is designed for identity verification (KYC), matching ID photos against live photos.

## 🚀 Features

- **High Accuracy**: Uses the **ArcFace** model combined with the **RetinaFace** detector for state-of-the-art performance.
- **Robust Detection**: Handles various lighting conditions and angles.
- **Multithreaded UI**: The interface remains responsive during the heavy computation of face verification.
- **Professional Logging**: results and errors are logged to `logs/verification.log`.
- **Centralized Configuration**: Easily tweak parameters in `config.py`.

## 🛠️ Technology Stack

- **Core**: Python 3.x
- **Deep Learning**: [DeepFace](https://github.com/serengil/deepface) (ArcFace model)
- **Face Detection**: RetinaFace
- **GUI**: Tkinter (Desktop)
- **Image Processing**: Pillow (PIL)

## 📦 Installation

1. Clone the repository or extract the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: On first run, the system will download the ArcFace and RetinaFace model weights (approx. 500MB).*

## 📖 Usage

Run the application:
```bash
python main.py
```

1. **Upload Photo 1**: Select an official ID photo or a clear source image.
2. **Upload Photo 2**: Select a live photo or the target image for comparison.
3. **Verify**: Click "START VERIFICATION". The system will process and display the result.

## 📁 Project Structure

- `main.py`: Application entry point.
- `ui.py`: Tkinter-based user interface.
- `verifier.py`: Core verification logic using DeepFace.
- `config.py`: Configuration settings (model, detection backend).
- `logger.py`: Logging setup.
- `logs/`: Directory for log files.

## ⚖️ License
This project is for internal identity verification purposes. Ensure compliance with local data privacy laws (e.g., GDPR/CCPA).
