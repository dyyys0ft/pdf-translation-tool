from PIL import Image
import os
import sys
import re

def images_to_pdf(images_folder, output_pdf=None):
    # Get all PNG images in folder
    files = [f for f in os.listdir(images_folder) if f.lower().endswith(".png")]
    
    if not files:
        print("⚠️ No PNG images found in folder:", images_folder)
        return
    
    # Sort numerically based on filename (e.g. 1.png, 2.png, 10.png)
    def extract_number(filename):
        match = re.search(r"(\d+)", filename)
        return int(match.group(1)) if match else float("inf")
    
    files.sort(key=extract_number)

    # Open first image
    first_image = Image.open(os.path.join(images_folder, files[0])).convert("RGB")
    
    # Open remaining images
    image_list = []
    for file in files[1:]:
        img_path = os.path.join(images_folder, file)
        img = Image.open(img_path).convert("RGB")
        image_list.append(img)
    
    # If output name not given, use folder name
    if output_pdf is None:
        output_pdf = os.path.basename(images_folder.rstrip("/\\")) + ".pdf"
    
    output_path = os.path.join(images_folder, output_pdf)
    first_image.save(output_path, save_all=True, append_images=image_list)
    
    print(f"✅ PDF created successfully: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python images_to_pdf.py <images_folder> [output.pdf]")
    else:
        folder = sys.argv[1]
        output_name = sys.argv[2] if len(sys.argv) > 2 else None
        images_to_pdf(folder, output_name)

images_to_pdf("downloads/","libro3_translated")