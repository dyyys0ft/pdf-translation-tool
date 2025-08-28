import win32clipboard as w
import win32con
from PIL import Image
import io

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


# Example usage
if __name__ == "__main__":
    copy_image_to_clipboard(
        r"C:\Users\dyane\OneDrive\Documentos\pdfEN_2_SP\translated_result.png"
    )
