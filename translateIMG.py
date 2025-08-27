import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# ⚙️ CONFIG
# If your file is inside a folder called "imgs" in the same directory as the script
IMAGE_PATH = os.path.abspath("imgs/1")

OUTPUT_WAIT = 1  # seconds to wait for translation

# Setup Chrome
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome( options=options)

try:
    # 1. Open Google Translate (Images)
    driver.get("https://translate.google.com/?hl=es&sl=auto&tl=es&op=images")
    wait = WebDriverWait(driver, 10)

    
    # 3. Upload file via hidden <input type="file">
    upload_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @name='file']"))
    )
    upload_input.send_keys(IMAGE_PATH)
    print(f"📤 Uploaded file: {IMAGE_PATH}")

    # 4. Wait for translation to finish rendering
    print("⏳ Waiting for translation...")
    time.sleep(OUTPUT_WAIT)

    # 5. Screenshot of result (full page for now)
    driver.save_screenshot("translated_result.png")
    print("✅ Saved screenshot: translated_result.png")
    

finally:
    driver.quit()

input()