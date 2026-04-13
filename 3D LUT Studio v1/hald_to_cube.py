import os

# CRITICAL: This must happen BEFORE import cv2
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import numpy as np

def convert_hald_to_cube(hald_path, cube_path, lut_size=256):
    print(f"Loading float HALD image: {hald_path}...")
    
    # Read with full 32-bit float precision intact
    img = cv2.imread(hald_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {hald_path}")

    # Convert BGR to RGB
    if len(img.shape) == 3 and img.shape[2] >= 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Enforce float processing
    if img.dtype == np.float32 or img.dtype == np.float64:
        print("32-bit Float EXR detected. Processing with zero integer quantization.")
    else:
        raise TypeError(f"Expected float32 EXR, but got {img.dtype}. Please ensure you rendered a 32-bit float EXR.")

    level = int(np.round(lut_size ** 0.5))
    expected_dim = level * lut_size

    if img.shape[0] != expected_dim or img.shape[1] != expected_dim:
        raise ValueError(f"Dimensionality mismatch. Expected {expected_dim}x{expected_dim} for a {lut_size}-point LUT.")

    total_points = lut_size**3
    print(f"Writing {total_points:,} lines to {cube_path}. This will take a moment...")
    
    with open(cube_path, 'w') as f:
        f.write(f"TITLE \"Extracted_HALD_{lut_size}_Float\"\n")
        f.write(f"LUT_3D_SIZE {lut_size}\n\n")

        for b in range(lut_size):
            block_x = b % level
            block_y = b // level
            
            for g in range(lut_size):
                for r in range(lut_size):
                    x = block_x * lut_size + r
                    y = block_y * lut_size + g

                    # Since it's an EXR, values are already mapped natively in the float space
                    rgb = img[y, x][:3]
                    
                    # Write the raw floating point math directly to the cube file
                    f.write(f"{rgb[0]:.6f} {rgb[1]:.6f} {rgb[2]:.6f}\n")

    print(f"Done! Massive mathematically pure LUT saved to {cube_path}")

if __name__ == "__main__":
    # Ensure this matches your exported EXR filename
    INPUT_HALD = "graded_hald_256.exr" 
    OUTPUT_CUBE = "extracted_256.cube"
    
    convert_hald_to_cube(INPUT_HALD, OUTPUT_CUBE, lut_size=256)