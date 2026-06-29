import os
from PIL import Image

IMAGE_PATH = r"C:\Users\worka\.gemini\antigravity\brain\40137a0a-53ba-4bd9-864a-0c5ff65493dd\media__1782758780566.png"
OUTPUT_PATH = r"C:\Users\worka\.gemini\antigravity\scratch\armourIQ-Workflow\frontend\src\app\icon.png"

def make_favicon():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Source image not found at {IMAGE_PATH}")
        return
        
    print(f"Opening source image: {IMAGE_PATH}")
    img = Image.open(IMAGE_PATH).convert("RGBA")
    datas = img.getdata()
    
    # 1. Convert white and near-white pixels to transparent
    new_data = []
    threshold = 240 # Threshold for white
    for item in datas:
        r, g, b, a = item
        # If pixel is near-white, make it transparent
        if r > threshold and g > threshold and b > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # 2. Crop to bounding box of non-transparent content
    # Find bounding box
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        print(f"Cropped content to bounding box: {bbox}")
        
    # 3. Make it a square (favicons look best when square)
    width, height = img.size
    max_size = max(width, height)
    
    # Create a square transparent background
    square_img = Image.new("RGBA", (max_size, max_size), (0, 0, 0, 0))
    # Paste cropped content in the center
    paste_x = (max_size - width) // 2
    paste_y = (max_size - height) // 2
    square_img.paste(img, (paste_x, paste_y))
    
    # 4. Save as high-res PNG (Next.js automatically resizes it to 16x16, 32x32, etc.)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    square_img.save(OUTPUT_PATH, "PNG")
    print(f"Favicon successfully saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    make_favicon()
