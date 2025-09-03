"""
1. convert all pdf pages to images and save it to a folder ✔
2. translate each image from language A to B
3. join all the generated images into a pdf file
"""

import shutil
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


def pdf_to_images(pdf_path, zoom=4):
    # Open PDF
    doc = fitz.open(pdf_path)
    book_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Create folder for images
    if not os.path.exists(book_name):
        os.makedirs(book_name)
    
    print(f"Converting '{pdf_path}' into images inside folder '{book_name}'...")
    
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Render page at high resolution (zoom factor)
        matrix = fitz.Matrix(zoom, zoom)  # 4x zoom = ~300-400 DPI
        pix = page.get_pixmap(matrix=matrix, alpha=False)  # type: ignore # Use getPixmap for older PyMuPDF versions
        
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

    

def images_to_pdf(images_folder, output_pdf=None):
    # Get all PNG images in folder (with full path)
    files = [os.path.join(images_folder, f) for f in os.listdir(images_folder) if f.lower().endswith(".png")]
    
    if not files:
        print("⚠️ No PNG images found in folder:", images_folder)
        return None

    # ✅ Sort by creation time (oldest first)
    files.sort(key=os.path.getctime)

    # Open first image
    first_image = Image.open(files[0]).convert("RGB")

    # Open remaining images
    image_list = [Image.open(f).convert("RGB") for f in files[1:]]

    # If output name not given, use folder name
    if output_pdf is None:
        output_pdf = os.path.basename(images_folder.rstrip("/\\")) + ".pdf"

    output_path = os.path.join(images_folder, output_pdf)

    # Save all images into a single PDF
    first_image.save(output_path, save_all=True, append_images=image_list)

    print(f"✅ PDF created successfully: {output_path}")
    return output_path



def delete_directory(path):
    """
    Delete a directory and all its contents.
    
    Args:
        path (str): Path to the directory.
    """
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
        print(f"✅ Deleted directory: {path}")
    else:
        print(f"⚠️ Directory does not exist: {path}")



BOOK_NAME = "lib2"
BOOK_PATH = BOOK_NAME + ".pdf"

pdf_to_images( pdf_path = BOOK_PATH)

setup_chrome_driver()


options = Options()
options.add_argument("--start-maximized")
driver = setup_chrome_driver()



count_translated_imgs = file_count = sum(1 for f in os.listdir(os.path.join(os.getcwd(), BOOK_NAME)) if f.lower().endswith(".png")) + 1
print(" ✅ number of files", count_translated_imgs)

driver.get("https://translate.google.com/?hl=es&sl=auto&tl=es&op=images")
wait = WebDriverWait(driver, 10)
driver.find_element(By.ID, "i59").click()

for i in range(1,count_translated_imgs):
        
        # 1. Open Google Translate (Images)
        path_source = os.path.join(os.getcwd(), BOOK_NAME+"\\"+str(i)+".png")        
        
        #click on english 
        time.sleep(3)
        
        #copy image to translate
        copy_image_to_clipboard(path_source)

        #paste image
        button = driver.find_element(By.XPATH, "//button//span[text()='Pegar desde el portapapeles']")
        print("✅ PEGAR DESDE EL PORTAPAPELES")
        button.click()
        
        #download image
        time.sleep(20)
        download_btn = driver.find_element(By.XPATH, "//button//span[text()='Descargar traducción']")
        download_btn.click()
        print("✅ DESCARGAR TRADUCCION")
        print("✅ Clicked 'Download translated image'")

        #delete image
        delete_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Borrar imagen']")
        delete_button.click()
        print("Clicked button!")
        

images_to_pdf("downloads/")
delete_directory("/"+BOOK_NAME)


