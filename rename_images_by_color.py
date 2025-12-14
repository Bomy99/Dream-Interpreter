#!/usr/bin/env python3
"""
Analyze PNG images and rename them based on their dominant color.
"""

import os
from pathlib import Path
from collections import Counter

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL/Pillow not available. Install with: pip install pillow numpy")

def get_dominant_color(image_path):
    """Get the dominant color from an image."""
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for faster processing
        img.thumbnail((100, 100))
        
        # Get pixel data
        pixels = np.array(img)
        pixels = pixels.reshape(-1, 3)
        
        # Remove transparent/white/black pixels (likely background)
        # Filter out very light pixels (likely transparent/white background)
        pixels = pixels[(pixels.sum(axis=1) < 750)]  # Remove very light pixels
        
        if len(pixels) == 0:
            # If all pixels filtered, use original
            pixels = np.array(img).reshape(-1, 3)
        
        # Get most common color
        # Round to nearest 10 to group similar colors
        rounded = (pixels // 10 * 10).astype(int)
        color_counts = Counter(tuple(c) for c in rounded)
        
        if color_counts:
            dominant_rgb = color_counts.most_common(1)[0][0]
            return dominant_rgb
        else:
            return (128, 128, 128)  # Default gray
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return (128, 128, 128)

def rgb_to_color_name(r, g, b):
    """Convert RGB to a descriptive color name."""
    # Color name mapping based on RGB ranges
    if r > 200 and g > 200 and b > 200:
        return "white"
    elif r < 50 and g < 50 and b < 50:
        return "black"
    elif r > g and r > b:
        if r > 200:
            if g > 150:
                return "orange"
            elif b > 150:
                return "pink"
            else:
                return "red"
        else:
            return "dark_red"
    elif g > r and g > b:
        if g > 200:
            return "green"
        elif g > 100:
            return "dark_green"
        else:
            return "very_dark_green"
    elif b > r and b > g:
        if b > 200:
            return "blue"
        elif b > 100:
            return "dark_blue"
        else:
            return "very_dark_blue"
    elif r > 150 and g > 150 and b < 100:
        return "yellow"
    elif r > 100 and g < 100 and b > 150:
        return "purple"
    elif r > 150 and g < 100 and b > 150:
        return "magenta"
    elif abs(r - g) < 30 and abs(g - b) < 30:
        if r > 150:
            return "light_gray"
        elif r > 100:
            return "gray"
        else:
            return "dark_gray"
    elif r > 150 and g > 100 and b < 100:
        return "brown"
    elif r > 200 and g > 200:
        return "light_yellow"
    elif r > 150 and b > 150:
        return "lavender"
    else:
        # Create a name from RGB values
        return f"mixed_{r//20}_{g//20}_{b//20}"

def rename_images_by_color(directory):
    """Rename all PNG files in directory based on their dominant color."""
    if not PIL_AVAILABLE:
        print("PIL/Pillow is required. Install with: pip install pillow numpy")
        return
    
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Directory not found: {directory}")
        return
    
    # Get all PNG files
    png_files = sorted(dir_path.glob("*.png"))
    
    if not png_files:
        print("No PNG files found in directory")
        return
    
    print(f"Found {len(png_files)} PNG files")
    print("Analyzing colors and renaming...\n")
    
    renamed = []
    for i, png_file in enumerate(png_files, 1):
        print(f"Processing {i}/{len(png_files)}: {png_file.name}")
        
        # Get dominant color
        rgb = get_dominant_color(png_file)
        color_name = rgb_to_color_name(*rgb)
        
        # Create new filename
        new_name = f"{color_name}_{rgb[0]}_{rgb[1]}_{rgb[2]}.png"
        new_path = dir_path / new_name
        
        # Handle duplicates
        counter = 1
        while new_path.exists() and new_path != png_file:
            new_name = f"{color_name}_{rgb[0]}_{rgb[1]}_{rgb[2]}_{counter}.png"
            new_path = dir_path / new_name
            counter += 1
        
        # Rename
        try:
            png_file.rename(new_path)
            renamed.append((png_file.name, new_name, color_name, rgb))
            print(f"  -> {new_name} (color: {color_name}, RGB: {rgb})")
        except Exception as e:
            print(f"  Error renaming: {e}")
    
    print(f"\nRenamed {len(renamed)} files")
    print("\nSummary:")
    for old, new, color, rgb in renamed:
        print(f"  {old} -> {new}")

if __name__ == "__main__":
    directory = r"C:\Users\Arno\Desktop\Freud\without background BOOK"
    rename_images_by_color(directory)
