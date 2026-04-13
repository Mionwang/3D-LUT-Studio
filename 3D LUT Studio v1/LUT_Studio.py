import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# CRITICAL: Enable EXR support before importing OpenCV
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

# --- 1. DEPENDENCY CHECKER ---
try:
    import cv2
    import numpy as np
    dependencies_met = True
except ImportError as e:
    dependencies_met = False
    missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)

def show_dependency_warning():
    root = tk.Tk()
    root.title("Missing Dependencies")
    root.geometry("550x250")
    root.configure(padx=20, pady=20)
    
    ttk.Label(root, text="⚠️ Required Libraries Missing", font=("Segoe UI", 16, "bold"), foreground="#d9534f").pack(anchor="w", pady=(0, 10))
    ttk.Label(root, text="To process massive 32-bit EXR math, this tool requires OpenCV and NumPy.", font=("Segoe UI", 10)).pack(anchor="w")
    ttk.Label(root, text="Please open Windows PowerShell and run the following command:", font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 5))
    
    cmd_entry = ttk.Entry(root, font=("Consolas", 11))
    cmd_entry.insert(0, "pip install opencv-python numpy")
    cmd_entry.state(['readonly'])
    cmd_entry.pack(fill="x", pady=(0, 15))
    
    ttk.Button(root, text="Exit", command=root.destroy).pack(anchor="e")
    root.eval('tk::PlaceWindow . center')
    root.mainloop()
    sys.exit()

if not dependencies_met:
    show_dependency_warning()

# --- 2. CORE MATH ENGINES ---
def generate_exr(lut_size, output_path, status_label, root):
    try:
        level = int(np.round(lut_size ** 0.5))
        img_dim = level * lut_size
        
        img = np.zeros((img_dim, img_dim, 3), dtype=np.float32)

        for b in range(lut_size):
            block_x = b % level
            block_y = b // level
            b_val = b / (lut_size - 1)
            
            for g in range(lut_size):
                g_val = g / (lut_size - 1)
                for r in range(lut_size):
                    r_val = r / (lut_size - 1)
                    x = block_x * lut_size + r
                    y = block_y * lut_size + g
                    img[y, x] = [b_val, g_val, r_val]

        cv2.imwrite(output_path, img, [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT])
        root.after(0, lambda: status_label.config(text=f"Success! {lut_size}-point EXR saved.", foreground="green"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Generation Error", str(e)))
        root.after(0, lambda: status_label.config(text="Error generating file.", foreground="red"))

def extract_cube(lut_size, input_path, output_path, status_label, root):
    try:
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None: raise FileNotFoundError("Could not load EXR file.")

        if len(img.shape) == 3 and img.shape[2] >= 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if img.dtype != np.float32 and img.dtype != np.float64:
            root.after(0, lambda: messagebox.showwarning("Precision Warning", "Image is not 32-bit float. Expect quantization rounding."))

        level = int(np.round(lut_size ** 0.5))
        
        with open(output_path, 'w') as f:
            f.write(f"TITLE \"Extracted_HALD_{lut_size}_Float\"\n")
            f.write(f"LUT_3D_SIZE {lut_size}\n\n")

            for b in range(lut_size):
                block_x = b % level
                block_y = b // level
                for g in range(lut_size):
                    for r in range(lut_size):
                        x = block_x * lut_size + r
                        y = block_y * lut_size + g
                        rgb = img[y, x][:3]
                        f.write(f"{rgb[0]:.6f} {rgb[1]:.6f} {rgb[2]:.6f}\n")

        root.after(0, lambda: status_label.config(text=f"Done! {lut_size}-point LUT extracted.", foreground="green"))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Extraction Error", str(e)))
        root.after(0, lambda: status_label.config(text="Error extracting LUT.", foreground="red"))

# --- 3. THE GUI APPLICATION ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("3D LUT / EXR Studio")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # UI Variables
        self.lut_size_var = tk.IntVar(value=144)
        
        self.build_ui()

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill="both", expand=True)

        # Header
        ttk.Label(main_frame, text="Mathematical LUT Processor", font=("Segoe UI", 16, "bold")).pack(anchor="center", pady=(0, 20))

        # Size Selector
        size_frame = ttk.LabelFrame(main_frame, text="1. Select Grid Density", padding="10 10 10 10")
        size_frame.pack(fill="x", pady=(0, 15))
        ttk.Radiobutton(size_frame, text="64-point (NLE Standard)", variable=self.lut_size_var, value=64).pack(side="left", padx=10)
        ttk.Radiobutton(size_frame, text="144-point (High Fidelity)", variable=self.lut_size_var, value=144).pack(side="left", padx=10)
        ttk.Radiobutton(size_frame, text="256-point (ML / Tensor)", variable=self.lut_size_var, value=256).pack(side="left", padx=10)

        # Generator Block
        gen_frame = ttk.LabelFrame(main_frame, text="2. Generate Identity Pattern", padding="10 10 10 10")
        gen_frame.pack(fill="x", pady=(0, 15))
        ttk.Button(gen_frame, text="Generate 32-bit EXR", command=self.handle_generate).pack(fill="x")

        # Extractor Block
        ext_frame = ttk.LabelFrame(main_frame, text="3. Extract .cube LUT", padding="10 10 10 10")
        ext_frame.pack(fill="x", pady=(0, 15))
        ttk.Button(ext_frame, text="Select Graded EXR & Compile", command=self.handle_extract).pack(fill="x")

        # Status Bar
        self.status_label = ttk.Label(main_frame, text="Ready.", font=("Segoe UI", 9, "italic"), foreground="gray")
        self.status_label.pack(side="bottom", anchor="w", pady=(10, 0))

    def handle_generate(self):
        size = self.lut_size_var.get()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".exr", 
            initialfile=f"identity_hald_{size}.exr",
            title="Save Identity EXR",
            filetypes=[("OpenEXR Image", "*.exr")]
        )
        if filepath:
            self.status_label.config(text=f"Generating {size}-point EXR... Please wait.", foreground="blue")
            threading.Thread(target=generate_exr, args=(size, filepath, self.status_label, self.root), daemon=True).start()

    def handle_extract(self):
        size = self.lut_size_var.get()
        input_file = filedialog.askopenfilename(title="Select Graded EXR", filetypes=[("OpenEXR Image", "*.exr")])
        if not input_file: return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".cube",
            initialfile=f"extracted_{size}.cube",
            title="Save Extracted LUT",
            filetypes=[("3D LUT File", "*.cube")]
        )
        if output_file:
            self.status_label.config(text=f"Compiling {size}-point LUT ({size**3} lines)...", foreground="blue")
            threading.Thread(target=extract_cube, args=(size, input_file, output_file, self.status_label, self.root), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.eval('tk::PlaceWindow . center')
    root.mainloop()