import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import threading
from verifier import verify_faces
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

        self.verify_btn = tk.Button(controls_frame, text="START VERIFICATION", font=("Helvetica", 12, "bold"), 
                                   bg="#27ae60", fg="white", width=25, height=2, command=self.start_verification_thread,
                                   relief="raised", cursor="hand2")
        self.verify_btn.pack(pady=10)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceVerifierApp(root)
    root.mainloop()