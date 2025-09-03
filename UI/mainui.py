import tkinter as tk
from tkinter import filedialog, ttk
import fitz  # PyMuPDF
import os, io, re, time
import win32clipboard as w
import win32con
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image

# ---------------- Utility Functions ---------------- #

def pdf_to_images(pdf_path, zoom=4):
    """Convert PDF into PNG images (one per page)."""
    doc = fitz.open(pdf_path)
    book_name = os.path.splitext(os.path.basename(pdf_path))[0]

    if not os.path.exists(book_name):
        os.makedirs(book_name)

    images = []
    for page_number in range(len(doc)):
        page = doc[page_number]
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False) # type: ignore
        output_path = os.path.join(book_name, f"{page_number + 1}.png")
        pix.save(output_path)
        images.append(output_path)

    doc.close()
    return images, book_name


def setup_chrome_driver(download_dir=None):
    if not download_dir:
        download_dir = os.path.join(os.getcwd(), "downloads")

    os.makedirs(download_dir, exist_ok=True)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--enable-features=ClipboardContentSetting")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "profile.default_content_setting_values.clipboard": 1,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def copy_image_to_clipboard(image_path: str):
    """Copy an image into the Windows clipboard."""
    image = Image.open(image_path)
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # strip BMP header
    output.close()

    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_DIB, data)
    w.CloseClipboard()


def images_to_pdf(images_folder, output_pdf=None):
    """Combine PNG images into a single PDF."""
    files = [f for f in os.listdir(images_folder) if f.lower().endswith(".png")]
    if not files:
        return

    def extract_number(filename):
        match = re.search(r"(\d+)", filename)
        return int(match.group(1)) if match else float("inf")

    files.sort(key=extract_number)

    first_image = Image.open(os.path.join(images_folder, files[0])).convert("RGB")
    image_list = [
        Image.open(os.path.join(images_folder, f)).convert("RGB") for f in files[1:]
    ]

    if output_pdf is None:
        output_pdf = os.path.basename(images_folder.rstrip("/\\")) + "_translated.pdf"

    output_path = os.path.join(images_folder, output_pdf)
    first_image.save(output_path, save_all=True, append_images=image_list)
    return output_path

# ---------------- Tkinter UI Functions ---------------- #

def choose_file():
    file_path = filedialog.askopenfilename(
        title="Choose PDF File", filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        file_output_var.set(file_path)

def start_translation():
    pdf_path = file_output_var.get()
    if not os.path.isfile(pdf_path):
        return

    # Reset UI
    progress_var.set(0)
    message_label.grid_remove()

    # Step 1: Convert PDF → images
    images, folder = pdf_to_images(pdf_path)
    total_steps = len(images)
    progress_bar.config(maximum=total_steps)

    # Step 2: Start Selenium
    driver = setup_chrome_driver()
    driver.get("https://translate.google.com/?hl=es&sl=auto&tl=es&op=images")
    time.sleep(3)

    # Step 3: Translate images one by one
    for idx, img_path in enumerate(images, start=1):
        copy_image_to_clipboard(img_path)
        button = driver.find_element(By.XPATH, "//button//span[text()='Pegar desde el portapapeles']")
        button.click()

        # wait for translation
        time.sleep(10)

        download_btn = driver.find_element(By.XPATH, "//button//span[text()='Descargar traducción']")
        download_btn.click()

        delete_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Borrar imagen']")
        delete_button.click()

        # Update progress bar
        progress_var.set(idx)
        step_counter.set(f"{idx}/{total_steps}")
        root.update_idletasks()

    driver.quit()

    # Step 4: Combine translated images into PDF
    final_pdf = images_to_pdf("downloads/")
    if final_pdf:
        message_label.config(text=f"The translation is done!\nSaved: {final_pdf}")
        message_label.grid(row=3, column=0, columnspan=3, pady=10)

# ---------------- Build Tkinter Window ---------------- #

root = tk.Tk()
root.title("Translation Tool")

# Title
title_label = tk.Label(root, text="Translation Tool", font=("Arial", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=3, pady=10)

# File chooser row
file_button = tk.Button(root, text="Choose File", command=choose_file)
file_button.grid(row=1, column=0, padx=10, pady=10)

file_output_var = tk.StringVar(value="No file chosen")
file_output_label = tk.Label(root, textvariable=file_output_var, width=40, anchor="w", relief="sunken")
file_output_label.grid(row=1, column=1, padx=10, pady=10)

# Progress bar + counter
progress_var = tk.IntVar(value=0)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate", variable=progress_var)
progress_bar.grid(row=1, column=2, padx=10, pady=10)

step_counter = tk.StringVar(value="0/0")
progress_text = tk.Label(root, textvariable=step_counter, font=("Arial", 10, "bold"), bg="white")
progress_text.place(in_=progress_bar, relx=0.5, rely=0.5, anchor="center")

# Start button
start_button = tk.Button(root, text="Start Translation", command=start_translation)
start_button.grid(row=2, column=0, columnspan=3, pady=10)

# Completion message
message_label = tk.Label(root, text="The translation is done!", fg="green", font=("Arial", 12, "bold"))
message_label.grid(row=3, column=0, columnspan=3, pady=10)
message_label.grid_remove()

root.mainloop()
