# 3D LUT Studio

A Python-based, high-precision 32-bit floating-point LUT generator and extractor. 

This tool allows colorists, technical directors, and machine learning researchers to generate "Identity HALD" images, grade them in standard NLEs (like DaVinci Resolve), and extract the mathematical changes into a standard 3D `.cube` LUT file. 

## ✨ Features
* **Clean GUI:** A standalone desktop interface—no command-line typing required after initial setup.
* **Variable Density:** Supports NLE standard sizes (64-point) up to hyper-dense ML/Tensor sizes (144-point and 256-point).
* **Precision Math:** Operates entirely in 32-bit float OpenEXR space, reading and writing raw `float32` data to preserve surgical curves and complex DCTL density math down to the decimal.
* **Automated Dependency Checking:** Prompts users with native UI installation instructions if they lack the required Python libraries.

---

## ⚙️ Prerequisites & Installation

This application requires **Python 3.x** to run. 

1. Clone or download this repository to your local machine.
2. Open your terminal or Windows PowerShell.
3. Install the required mathematical and image-processing libraries by running:

    pip install opencv-python numpy

---

## 🚀 How to Use

The workflow is broken down into three simple phases: Generate, Grade, and Extract.

### Phase 1: Generate the Identity Pattern
1. Double-click the `LUT_Studio.py` script to launch the GUI (or run `python LUT_Studio.py` from your terminal).
2. Under **Select Grid Density**, choose your desired LUT size:
   * **64-point:** Best for standard real-time video editing.
   * **144-point:** Best for high-fidelity offline rendering.
   * **256-point:** Best for Machine Learning/AI image conditioning.
3. Click **Generate 32-bit EXR**.
4. Choose a save location. The script will output a geometrically perfect, neutral EXR image representing a 3D color cube.

### Phase 2: Apply Your Grade
1. Import the generated `.exr` file into your grading software of choice (e.g., DaVinci Resolve, Nuke, or After Effects).
2. Apply your color grades, complex node trees, DCTLs, or surgical curves.
3. **Render the result out as an OpenEXR image.**

> **⚠️ CRITICAL DAVINCI RESOLVE SETTINGS:**
> EXR files default to linear gamma. Ensure the EXR export is explicitly set to **32-bit float** (*not* 16-bit half-float) to preserve the math.

### Phase 3: Extract the .cube LUT
1. Back in the Python GUI, ensure your target grid density matches the file you just generated.
2. Click **Select Graded EXR & Compile**.
3. Select your exported EXR file from your grading software.
4. Choose a save destination for your final `.cube` file.
5. *Note: The extraction runs in the background. Massive LUTs (like 256-point) require compiling over 16.7 million lines of text, which may take a minute or two. The status bar will update to "Done!" when finished.*

---

## ⚠️ Important Note on Massive LUTs (256-Point)

Standard NLEs (Premiere, Resolve, Final Cut) are not necessarily designed to read half-gigabyte `.cube` files, though Resolve Studio on my workstation handles them just fine. If you attempt to load a 256-point LUT into DaVinci Resolve, the LUT parser may freeze, crash, or fallback to a lower-quality interpolation method.

* If your goal is **real-time NLE grading**, stick to **64-point** or **144-point** and let the software's native 32-bit tetrahedral interpolation handle the gradients. 
* **256-point LUTs** are strictly intended for data science, AI generation pipelines, or ground-truth tensor conversion where a GPU can load the massive matrix directly into VRAM.

---

## 🛠️ Troubleshooting

**"The script flashes and closes immediately when I try to run it!"**
This usually means Python isn't added to your system's PATH, or you are missing the required libraries. Open PowerShell, navigate to the folder, and run `python LUT_Studio.py` manually to see the specific error readout.

**"My extracted LUT looks completely wrong/blown out in Resolve!"**
You likely exported your EXR from Resolve with a color space transform applied on the delivery page. EXRs are linear by nature; if you export with a Rec.709 tag, the LUT will permanently inherit a double-gamma curve. Ensure your export settings bypass all output color space tagging.

---

## 📄 I made it using Gemini. Use it for whatever you like. Don't sell it though.
