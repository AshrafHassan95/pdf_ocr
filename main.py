import os
import pytesseract
import cv2
from PIL import Image
from pdf2image import convert_from_path
from PyPDF2 import PdfMerger
import io

# =============================
# CONFIG
# =============================

INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"

# Windows users: uncomment if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

SUPPORTED_IMAGES = (".png", ".jpg", ".jpeg", ".tif", ".tiff")
SUPPORTED_PDFS = (".pdf",)

LANGUAGE = "eng"

# =============================
# HELPERS
# =============================

def ensure_dirs():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return gray


def image_to_searchable_pdf(image_path, output_pdf):
    img = cv2.imread(image_path)
    img = preprocess(img)

    pil_img = Image.fromarray(img)

    pdf_bytes = pytesseract.image_to_pdf_or_hocr(
        pil_img,
        lang=LANGUAGE,
        extension="pdf"
    )

    with open(output_pdf, "wb") as f:
        f.write(pdf_bytes)


def pdf_to_searchable_pdf(pdf_path, output_pdf):
    pages = convert_from_path(pdf_path, dpi=300)

    merger = PdfMerger()

    for page_num, page in enumerate(pages, start=1):
        print(f"  OCR page {page_num}/{len(pages)}")

        pdf_bytes = pytesseract.image_to_pdf_or_hocr(
            page,
            lang=LANGUAGE,
            extension="pdf"
        )

        pdf_stream = io.BytesIO(pdf_bytes)
        merger.append(pdf_stream)

    with open(output_pdf, "wb") as f:
        merger.write(f)

    merger.close()

# =============================
# MAIN
# =============================

def batch_ocr_to_pdf():
    ensure_dirs()

    for filename in os.listdir(INPUT_DIR):
        input_path = os.path.join(INPUT_DIR, filename)
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        output_pdf = os.path.join(OUTPUT_DIR, f"{name}_OCR.pdf")

        print(f"\nProcessing: {filename}")

        try:
            if ext in SUPPORTED_IMAGES:
                image_to_searchable_pdf(input_path, output_pdf)

            elif ext in SUPPORTED_PDFS:
                pdf_to_searchable_pdf(input_path, output_pdf)

            else:
                print(f"Skipped unsupported file: {filename}")
                continue

            print(f"Saved searchable PDF → {output_pdf}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    batch_ocr_to_pdf()
