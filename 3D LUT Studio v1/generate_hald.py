import os
# CRITICAL: This must happen BEFORE import cv2
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import numpy as np

def generate_float_hald(lut_size=256, output_filename="identity_hald_256.exr"):
    level = int(np.round(lut_size ** 0.5))
    img_dim = level * lut_size

    print(f"Generating {lut_size}-point 32-bit float HALD ({img_dim}x{img_dim})...")

    # Create an empty 32-bit float image matrix
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

    # Save as 32-bit EXR
    cv2.imwrite(output_filename, img, [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT])
    print(f"Success! Saved pure 32-bit float identity pattern to {output_filename}")

if __name__ == "__main__":
    generate_float_hald(lut_size=256, output_filename="identity_hald_256.exr")