import pytesseract
from PIL import Image

# Tesseract ka path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_text(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


# Testing
if __name__ == "__main__":
    image_path = r"C:\Users\lenovo\OneDrive\Desktop\STUCHECK_AI\test.jpg.jpeg"

    text = extract_text(r"C:\Users\lenovo\OneDrive\Desktop\STUCHECK_AI\test.jpg.jpeg")

    print("\n========== STUCHECK AI ==========")
    print("Extracted Document Text:")
    print("================================")
    print(text)