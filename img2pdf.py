import fitz  # PyMuPDF
import os
import sys

def pdf_to_images(pdf_path , zoom=4):
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
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        
        # Save image
        output_path = os.path.join(book_name, f"{page_number + 1}.png")
        pix.save(output_path)
        print(f"Saved: {output_path}")
    
    doc.close()
    print("All pages converted successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_images.py <your_pdf_file>")
    else:
        pdf_to_images(sys.argv[1])


pdf_to_images( pdf_path = "libro4.pdf")
