import os
import fitz
from PIL import Image
from io import BytesIO

def generate_pdf_cover(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count > 0:
            # Get first page and render at higher quality
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Resize to standard cover size while maintaining aspect ratio
            target_height = 600
            aspect_ratio = pix.width / pix.height
            target_width = int(target_height * aspect_ratio)
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Save as JPEG with high quality
            img.save(output_path, "JPEG", quality=95)
            print(f"Generated cover for {os.path.basename(pdf_path)}")
            return True
    except Exception as e:
        print(f"Error generating cover for {pdf_path}: {e}")
    return False

def main():
    # Create static/covers directory if it doesn't exist
    covers_dir = os.path.join(os.path.dirname(__file__), "static", "covers")
    os.makedirs(covers_dir, exist_ok=True)
    
    # PDF files and their corresponding cover names
    pdf_covers = {
        "docs/Performance Summary.pdf": "performance_summary.jpg",
        "docs/SDS document of writeshelf.pdf": "sds.jpg",
        "docs/SRS document of Writeshelf.pdf": "srs.jpg",
        "docs/WriteShelf - Functional Documentation.pdf": "functional_doc.jpg",
        "docs/reflections on the work done.pdf": "reflections.jpg"
    }
    
    # Generate covers
    for pdf_path, cover_name in pdf_covers.items():
        pdf_full_path = os.path.join(os.path.dirname(__file__), pdf_path)
        cover_full_path = os.path.join(covers_dir, cover_name)
        
        if os.path.exists(pdf_full_path):
            generate_pdf_cover(pdf_full_path, cover_full_path)
        else:
            print(f"PDF file not found: {pdf_full_path}")

if __name__ == "__main__":
    main()
