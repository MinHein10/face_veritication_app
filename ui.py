import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
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

    def load_and_display(self, path, panel):
        try:
            # Open and resize image
            img = Image.open(path)
            # Use fixed size from config for preview
            img = img.resize(config.IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            img_tk = ImageTk.PhotoImage(img)
            
            # CRITICAL: Remove width/height constraints before showing image to avoid label clipping
            panel.configure(image=img_tk, text="", width=0, height=0)
            
            # Keep reference to avoid garbage collection
            panel.image = img_tk 
            
            logger.info(f"Successfully displayed preview for: {path}")
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

        if "error" in result and result["distance"] in ["Error", "N/A"]:
            self.result_label.config(text="No Face Detected!", fg="#e67e22")
            messagebox.showwarning("Notice", result["error"])
        elif result.get("verified"):
            self.result_label.config(text="MATCH VERIFIED ✅", fg="#27ae60")
            self.score_label.config(text=f"Confidence Score (Cosine Distance): {result['distance']:.4f}")
        else:
            self.result_label.config(text="IDENTITY MISMATCH ❌", fg="#c0392b")
            self.score_label.config(text=f"Confidence Score (Cosine Distance): {result['distance']:.4f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceVerifierApp(root)
    root.mainloop()