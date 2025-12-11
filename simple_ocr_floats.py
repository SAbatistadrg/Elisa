import pyautogui
import time
from pathlib import Path
from PIL import ImageGrab
import pytesseract
import cv2
import numpy as np
import re
import shutil

# Configura caminho do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'D:\Users\igor.batista\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class SimpleOCRFloats:
    def __init__(self):
        self.save_path = Path("./salvos")

        # Limpa pasta salvos
        if self.save_path.exists():
            shutil.rmtree(self.save_path)
            print("🗑️  Pasta ./salvos limpa")
        self.save_path.mkdir(exist_ok=True)

    def _capture_and_save(self, filename):
        """Captura tela e salva"""
        screenshot = ImageGrab.grab()
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        filepath = self.save_path / filename
        cv2.imwrite(str(filepath), img)
        print(f"📸 Screenshot salvo: {filename}")
        return img

    def _go_to_top(self):
        """Vai pro topo (Home)"""
        print("🏠 Indo para o topo...")
        screen_width, screen_height = pyautogui.size()
        pyautogui.click(screen_width // 2, screen_height // 2)
        time.sleep(0.3)
        pyautogui.press('home')
        time.sleep(0.5)
        print("✅ Página no topo")

    def _page_down(self):
        """Aperta PgDn"""
        print("⬇️  Apertando Page Down...")
        pyautogui.press('pagedown')
        time.sleep(0.5)

    def _extract_floats_from_image(self, img, img_name):
        """Extrai todos os floats da imagem"""
        # Preprocessamento
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)

        # Salva preprocessado
        prep_path = self.save_path / f"prep_{img_name}"
        cv2.imwrite(str(prep_path), thresh)

        # OCR
        text = pytesseract.image_to_string(thresh, config='--psm 6 --oem 3')
        print(f"\n📝 Texto bruto de {img_name}:")
        print(text[:200] + "..." if len(text) > 200 else text)

        # Extrai floats com regex
        # Padrões: 10.5, 0.3, 5.0, etc
        float_pattern = r'\b\d+\.?\d*\b'
        matches = re.findall(float_pattern, text)

        # Converte pra float e filtra
        floats = []
        for match in matches:
            try:
                f = float(match)
                floats.append(f)
            except ValueError:
                continue

        return floats

    def read_floats(self):
        """Captura screenshots e extrai floats"""
        print("\n📸 Capturando screenshots...")

        # Screenshot 1: após Home
        self._go_to_top()
        img1 = self._capture_and_save("screenshot_1_home.png")
        floats1 = self._extract_floats_from_image(img1, "screenshot_1_home.png")

        # Screenshot 2: após PgDn
        self._page_down()
        img2 = self._capture_and_save("screenshot_2_pgdn.png")
        floats2 = self._extract_floats_from_image(img2, "screenshot_2_pgdn.png")

        # Combina todos os floats
        all_floats = floats1 + floats2

        print(f"\n✅ Floats encontrados no screenshot 1: {floats1}")
        print(f"✅ Floats encontrados no screenshot 2: {floats2}")
        print(f"\n📊 Total de floats encontrados: {len(all_floats)}")
        print(f"🔢 Todos os floats: {all_floats}")

        return all_floats
