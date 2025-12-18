# ocr_analyzer.py
import easyocr
from pathlib import Path
import re
import cv2

class OCRAnalyzer:
    def __init__(self):
        print("🔄 Carregando EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=True)
        print("✓ EasyOCR carregado\n")

    def extract_slider_value(self, image_path):
        """Extrai o valor numérico do slider"""
        try:
            # Carrega e AUMENTA a imagem 2x
            img = cv2.imread(str(image_path))
            img_large = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            # Roda OCR na imagem aumentada
            results = self.reader.readtext(img_large)

            # Procura apenas por números
            for (bbox, text, confidence) in results:
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    return float(numbers[0])

            return "N/A"
        except Exception as e:
            return "ERROR"

    def _extract_number_from_filename(self, filename):
        """Extrai o número do nome do arquivo pos-templateX.png"""
        match = re.search(r'pos-template(\d+)', filename.stem)
        return int(match.group(1)) if match else 0

    def analyze_all_crops(self, crops_dir="./salvos"):
        """Analisa todos os recortes pos-template"""
        crops_dir = Path(crops_dir)
        crop_files = list(crops_dir.glob("pos-template*.png"))

        if not crop_files:
            print("❌ Nenhum recorte encontrado")
            return []

        crop_files = sorted(crop_files, key=self._extract_number_from_filename)
        values = []

        for crop_file in crop_files:
            value = self.extract_slider_value(crop_file)
            values.append(value)

        # Se tiver mais de 3 valores, pega primeiro e último
        if len(values) > 3:
            x1 = values[0]
            x3 = values[-1]
            values = [x1, 0.00, x3]

        # Printa só a lista
        print("Valores extraídos:", values)
        return values
