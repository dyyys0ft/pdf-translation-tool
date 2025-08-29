import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import win32clipboard as w
import win32con
from PIL import Image
import io

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


# If your file is inside a folder called "imgs" in the same directory as the script
IMAGE_PATH = os.path.abspath("imgs/1")

OUTPUT_WAIT = 1  # seconds to wait for translation

# Setup Chrome
options = Options()
options.add_argument("--start-maximized")
driver = setup_chrome_driver()

translate_image(os.path.join(os.getcwd(), "./imgs/1.png"),"/translated images","2t")