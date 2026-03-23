import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk, ImageDraw
import threading
from verifier import verify_faces, get_face_embedding
from deepface import DeepFace
from database import db
import config
from logger import logger

class FaceVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        self.root.configure(bg="#f0f0f0")

        self.img1_path = None
        self.img2_path = None

        # UI Elements declaration
        self.frame1 = None
        self.panel1 = None
        self.frame2 = None
        self.panel2 = None
        self.verify_btn = None
        self.status_label = None
        self.result_label = None
        self.score_label = None

        self.setup_ui()

        # Start model pre-loading in a background thread
        threading.Thread(target=self.preload_models, daemon=True).start()

    def preload_models(self):
        """Pre-loads DeepFace models so the first verification is fast."""
        try:
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text="System initializing: Loading AI models...")

            logger.info(f"Background pre-loading model: {config.MODEL_NAME}")
            # This identifies the model and detector to use
            DeepFace.build_model(config.MODEL_NAME)

            logger.info("Background model loading complete.")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text="Ready")
        except Exception as e:
            logger.error(f"Error pre-loading models: {e}")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text="Initialization error. Check logs.")


    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x")
        tk.Label(header, text="PROFESSIONAL FACE VERIFICATION", font=("Helvetica", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=15)

        # Main Layout
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Image Containers
        img_frame = tk.Frame(main_frame, bg="#f0f0f0")
        img_frame.pack()

        # Left Panel (ID Photo)
        self.frame1 = tk.LabelFrame(img_frame, text="Photo 1 (ID/Source)", padx=10, pady=10, bg="white")
        self.frame1.grid(row=0, column=0, padx=20)
        self.panel1 = tk.Label(self.frame1, text="No Image Uploaded", bg="#ecf0f1", width=30, height=15)
        self.panel1.pack()
        tk.Button(self.frame1, text="Select Photo 1", command=self.upload_img1, bg="#34495e", fg="white", relief="flat", padx=10).pack(pady=10)

        # Right Panel (Live Photo)
        self.frame2 = tk.LabelFrame(img_frame, text="Photo 2 (Verification Target)", padx=10, pady=10, bg="white")
        self.frame2.grid(row=0, column=1, padx=20)
        self.panel2 = tk.Label(self.frame2, text="No Image Uploaded", bg="#ecf0f1", width=30, height=15)
        self.panel2.pack()
        tk.Button(self.frame2, text="Select Photo 2", command=self.upload_img2, bg="#34495e", fg="white", relief="flat", padx=10).pack(pady=10)

        # Controls & Status
        controls_frame = tk.Frame(self.root, bg="#f0f0f0")
        controls_frame.pack(pady=10)

        self.register_btn = tk.Button(controls_frame, text="REGISTER ID (DB)", font=("Helvetica", 10, "bold"),
                                   bg="#2980b9", fg="white", width=20, height=2, command=self.start_register_thread,
                                   relief="raised", cursor="hand2")
        self.register_btn.grid(row=0, column=0, padx=10, pady=5)

        self.verify_btn = tk.Button(controls_frame, text="1:1 VERIFY", font=("Helvetica", 10, "bold"),
                                   bg="#27ae60", fg="white", width=20, height=2, command=self.start_verification_thread,
                                   relief="raised", cursor="hand2")
        self.verify_btn.grid(row=0, column=1, padx=10, pady=5)

        self.recognize_btn = tk.Button(controls_frame, text="RECOGNIZE (DB)", font=("Helvetica", 10, "bold"),
                                   bg="#8e44ad", fg="white", width=20, height=2, command=self.start_recognize_thread,
                                   relief="raised", cursor="hand2")
        self.recognize_btn.grid(row=0, column=2, padx=10, pady=5)

        self.status_label = tk.Label(self.root, text="Ready", bd=1, relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x")

        # Result Display
        self.result_label = tk.Label(self.root, text="", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
        self.result_label.pack(pady=5)

        self.score_label = tk.Label(self.root, text="", font=("Helvetica", 10), bg="#f0f0f0")
        self.score_label.pack()

    def load_and_display(self, path, panel, facial_area=None):
        """
        Loads an image, optionally draws a bounding box, and displays it.
        """
        try:
            img = Image.open(path).convert("RGB")

            # Draw bounding box if provided (Visual Debugging)
            if facial_area:
                draw = ImageDraw.Draw(img)
                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
                # Draw a bright green rectangle with thickness
                for i in range(4): # Simulating thickness
                    draw.rectangle([x-i, y-i, x+w+i, y+h+i], outline="#00ff00")
                logger.info(f"Drew bounding box at {facial_area}")

            # Resize for UI
            img = img.resize(config.IMAGE_SIZE, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            panel.configure(image=img_tk, text="", width=0, height=0)
            panel.image = img_tk

        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            messagebox.showerror("Error", f"Could not load image: {e}")

    def upload_img1(self):
        self.img1_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if self.img1_path:
            self.load_and_display(self.img1_path, self.panel1)

    def upload_img2(self):
        self.img2_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if self.img2_path:
            self.load_and_display(self.img2_path, self.panel2)

    def start_verification_thread(self):
        if not self.img1_path or not self.img2_path:
            messagebox.showwarning("Incomplete Data", "Please upload both images first.")
            return

        self.verify_btn.config(state="disabled", text="PROCESSING...", bg="#95a5a6")
        self.status_label.config(text="Extracting features and comparing faces...")
        self.result_label.config(text="")
        self.score_label.config(text="")

        thread = threading.Thread(target=self.run_verification)
        thread.start()

    def run_verification(self):
        result = verify_faces(self.img1_path, self.img2_path)
        # Update UI in main thread
        self.root.after(0, lambda: self.show_result(result))

    def show_result(self, result):
        self.verify_btn.config(state="normal", text="START VERIFICATION", bg="#27ae60")
        self.status_label.config(text="Verification completed.")

        # Check for facial areas to implement Visual Debugging
        facial_areas = result.get("facial_areas", {})
        if 'img1' in facial_areas:
            self.load_and_display(self.img1_path, self.panel1, facial_areas['img1'])
        if 'img2' in facial_areas:
            self.load_and_display(self.img2_path, self.panel2, facial_areas['img2'])

        # Build detailed score text for quality
        quality_txt = ""
        if 'quality' in result:
            q1 = result['quality']['img1']
            q2 = result['quality']['img2']
            quality_txt = f"\nQuality Diagnostics:\nImg1 Blur: {q1['blur_score']:.1f}, Brightness: {q1['brightness_score']:.1f}\nImg2 Blur: {q2['blur_score']:.1f}, Brightness: {q2['brightness_score']:.1f}"

        if "error" in result and result.get("distance") in ["Error", "N/A"]:
            self.result_label.config(text="Assessment Failed!", fg="#e67e22")
            messagebox.showwarning("Notice", result["error"])
            self.score_label.config(text=result["error"])
        elif result.get("verified"):
            self.result_label.config(text="MATCH VERIFIED ✅", fg="#27ae60")
            self.score_label.config(text=f"Confidence Score (Cosine Distance): {result['distance']:.4f}" + quality_txt)
        else:
            self.result_label.config(text="IDENTITY MISMATCH ❌", fg="#c0392b")
            distance = result.get('distance')
            if isinstance(distance, (int, float)):
                self.score_label.config(text=f"Confidence Score (Cosine Distance): {distance:.4f}" + quality_txt)
            else:
                self.score_label.config(text=f"Confidence Score: {distance}")

    def start_register_thread(self):
        if not self.img1_path:
            messagebox.showwarning("Incomplete Data", "Please upload Photo 1 (ID) to register.")
            return

        user_id = simpledialog.askstring("Input", "Enter a User ID for this face:", parent=self.root)
        if not user_id:
            return

        self.register_btn.config(state="disabled", text="REGISTERING...", bg="#95a5a6")
        self.status_label.config(text="Extracting face and saving to database...")
        self.result_label.config(text="")
        self.score_label.config(text="")

        thread = threading.Thread(target=self.run_register, args=(user_id,))
        thread.start()

    def run_register(self, user_id):
        extraction = get_face_embedding(self.img1_path, is_source=True)
        if not extraction["success"]:
            self.root.after(0, lambda: self.show_register_result(False, extraction["error"]))
            return

        success, msg = db.add_face(user_id, extraction["embedding"], metadata={"source": "desktop_ui"})
        self.root.after(0, lambda: self.show_register_result(success, msg))

    def show_register_result(self, success, msg):
        self.register_btn.config(state="normal", text="REGISTER ID (DB)", bg="#2980b9")
        self.status_label.config(text="Database action completed.")

        if success:
            self.result_label.config(text="REGISTRATION SUCCESS ✅", fg="#27ae60")
            self.score_label.config(text=msg)
            messagebox.showinfo("Success", msg)
        else:
            self.result_label.config(text="REGISTRATION FAILED ❌", fg="#c0392b")
            self.score_label.config(text=msg)
            messagebox.showwarning("Notice", msg)

    def start_recognize_thread(self):
        if not self.img2_path:
            messagebox.showwarning("Incomplete Data", "Please upload Photo 2 for recognition.")
            return

        self.recognize_btn.config(state="disabled", text="SEARCHING...", bg="#95a5a6")
        self.status_label.config(text="Searching database for match...")
        self.result_label.config(text="")
        self.score_label.config(text="")

        thread = threading.Thread(target=self.run_recognize)
        thread.start()

    def run_recognize(self):
        extraction = get_face_embedding(self.img2_path, is_source=False)
        if not extraction["success"]:
            self.root.after(0, lambda: self.show_recognize_result({"verified": False, "match": None, "distance": "N/A", "error": extraction["error"]}))
            return

        result = db.search_face(extraction["embedding"])
        self.root.after(0, lambda: self.show_recognize_result(result))

    def show_recognize_result(self, result):
        self.recognize_btn.config(state="normal", text="RECOGNIZE (DB)", bg="#8e44ad")
        self.status_label.config(text="Search completed.")

        err = result.get("error")
        if err and result.get("distance") in ["Error", "N/A"]:
            self.result_label.config(text="SEARCH FAILED!", fg="#e67e22")
            messagebox.showwarning("Notice", err)
            self.score_label.config(text=err)
        elif result.get("verified"):
            self.result_label.config(text="IDENTITY FOUND ✅", fg="#27ae60")
            msg = f"Match: {result['match']} \nConfidence Score (Distance): {result['distance']:.4f}"
            self.score_label.config(text=msg)
        else:
            self.result_label.config(text="NO MATCH FOUND ❌", fg="#c0392b")
            if result.get("distance", "N/A") != "N/A":
                msg = f"No match within threshold. Closest was {result.get('closest_id')} at distance {result.get('distance'):.4f}"
            else:
                msg = result.get("error", "Not found.")
            self.score_label.config(text=msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceVerifierApp(root)
    root.mainloop()
