"""
1. convert all pdf pages to images and save it to a folder ✔
2. translate each image from language A to B
3. join all the generated images into a pdf file
"""

import fitz  # PyMuPDF
import sys
import time
import os
import io
import re
import win32clipboard as w
import win32con
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image



def pdf_to_images(pdf_path , zoom=4):
    # Open PDF
    doc = fitz.open(pdf_path) # type: ignore
    book_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Create folder for images
    if not os.path.exists(book_name):
        os.makedirs(book_name)
    
    print(f"Converting '{pdf_path}' into images inside folder '{book_name}'...")
    
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Render page at high resolution (zoom factor)
        matrix = fitz.Matrix(zoom, zoom)  # type: ignore # 4x zoom = ~300-400 DPI
        pix = page.get_pixmap(matrix=matrix, alpha=False) # type: ignore
        
        # Save image
        output_path = os.path.join(book_name, f"{page_number + 1}.png")
        pix.save(output_path)
        print(f"Saved: {output_path}")
    
    doc.close()
    print("All pages converted successfully!")


def setup_chrome_driver(download_dir = None):
    options = webdriver.ChromeOptions()
    if not download_dir:
        download_dir = os.path.join(os.getcwd(), "downloads")

    os.makedirs(download_dir, exist_ok=True)
    # This flag allows sites to read/write clipboard (so paste works)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--enable-features=ClipboardContentSetting")
    options.add_experimental_option(
        "prefs", {
            "download.default_directory": download_dir,
            "profile.default_content_setting_values.clipboard": 1,
            "download.prompt_for_download": False,        # disable "Ask where to save"
            "download.directory_upgrade": True,           # allow overwriting old files
            "safebrowsing.enabled": True                  # avoid warnings
        }
    )


    service = Service()  # optional: pass chromedriver path
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def copy_image_to_clipboard(image_path: str):
    """
    Copy an image (PNG, JPG, etc.) into the Windows clipboard
    so it can be pasted into apps (Paint, Word, etc).
    """
    # Open image with Pillow
    image = Image.open(image_path)

    # Convert to DIB (Device Independent Bitmap)
    output = io.BytesIO()
    # Must be BMP for Windows, no header (raw DIB format)
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # strip BMP header, keep DIB data
    output.close()

    # Set clipboard data
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_DIB, data)
    w.CloseClipboard()

    print(f"✅ Image copied to clipboard: {image_path}")


def translate_image(path_source, path_target, file_name):
    
    try:
        # 1. Open Google Translate (Images)
        driver.get("https://translate.google.com/?hl=es&sl=auto&tl=es&op=images")
        wait = WebDriverWait(driver, 10)

        #click on english 
        time.sleep(3)
        driver.find_element(By.ID, "i59").click()

        #copy image to translate
        copy_image_to_clipboard(path_source)

        #paste image
        time.sleep(3)
        button = driver.find_element(By.XPATH, "//button//span[text()='Pegar desde el portapapeles']")
        button.click()
        
        time.sleep(4)
        #download image
        download_btn = driver.find_element(By.XPATH, "//button//span[text()='Descargar traducción']")
        download_btn.click()
        print("✅ Clicked 'Download translated image'")
        print(f"✅ Saved screenshot: {path_target}/{file_name}")
        
    finally:

        driver.quit()

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


BOOK_PATH = ("./pdf book/libro1.pdf") 

#pdf_to_images( pdf_path = BOOK_PATH)

setup_chrome_driver()


options = Options()
options.add_argument("--start-maximized")
driver = setup_chrome_driver()

count_translated_imgs = 4

for i in range(1,count_translated_imgs):
  translate_image(os.path.join(os.getcwd(), "libro1\\"+str(i)+".png"),"\\translated images","2t") #change this

images_to_pdf("downloads/")

