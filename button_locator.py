# button_locator.py

import pyautogui
import easyocr
import ollama
from PIL import ImageGrab
import cv2
import numpy as np

class ButtonLocator:
    def __init__(self, llm_model="gemma3:12b"):
        self.llm_model = llm_model
        self.ocr_reader = easyocr.Reader(['pt', 'en'])
        self.last_found_coords = None
        self.last_ocr_coords = None

    def capture_screen(self):
        """Captura screenshot da tela"""
        screenshot = ImageGrab.grab()
        return screenshot

    def find_text_with_ocr(self, screenshot, target_text):
        """Encontra texto na tela e retorna coordenadas aproximadas"""
        img_array = np.array(screenshot)
        results = self.ocr_reader.readtext(img_array)
        for (bbox, text, confidence) in results:
            if target_text.lower() in text.lower():
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                center_x = sum(x_coords) / 4
                center_y = sum(y_coords) / 4
                return {
                    'found': True,
                    'x': int(center_x),
                    'y': int(center_y),
                    'confidence': confidence,
                    'bbox': bbox
                }
        return {'found': False}

    def validate_with_llm(self, screenshot, region, button_name):
        """Valida se a região contém o botão usando Vision LLM"""
        x, y = region['x'], region['y']
        margin = 100
        cropped = screenshot.crop((
            max(0, x - margin),
            max(0, y - margin),
            x + margin,
            y + margin
        ))
        cropped.save('temp_region.png')
        prompt = f"Nesta imagem, existe um botão com o texto '{button_name}'? Responda apenas 'sim' ou 'não'."
        response = ollama.chat(
            model=self.llm_model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': ['temp_region.png']
            }]
        )
        answer = response['message']['content'].lower()
        return 'sim' in answer

    def find_with_template(self, screenshot, template_path):
        """Tenta localizar usando template matching"""
        screen_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path)

        if template is None:
            return {'found': False}

        result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.7:
            template_h, template_w = template.shape[:2]
            center_x = max_loc[0] + template_w // 2
            center_y = max_loc[1] + template_h // 2
            return {
                'found': True,
                'x': center_x,
                'y': center_y,
                'confidence': max_val
            }
        return {'found': False}

    def locate_tm(self, button_name, use_template=None, validate_llm=True):
        """Localiza o botão sem clicar: Template primeiro, depois OCR+LLM"""
        print(f"🔍 Procurando botão: {button_name}")

        screenshot = self.capture_screen()

        if use_template:
            print("🔍 Tentando Template Matching...")
            template_result = self.find_with_template(screenshot, use_template)
            if template_result['found']:
                print(f"✓ Template encontrado em: ({template_result['x']}, {template_result['y']})")
                self.last_found_coords = template_result
                return template_result
            else:
                print("❌ Template não encontrou")

        print("🔍 Tentando OCR + LLM...")
        ocr_result = self.find_text_with_ocr(screenshot, button_name)

        if not ocr_result['found']:
            print("❌ Texto não encontrado via OCR")
            return False

        print(f"✓ OCR encontrou em: ({ocr_result['x']}, {ocr_result['y']})")
        self.last_ocr_coords = ocr_result

        if validate_llm:
            is_valid = self.validate_with_llm(screenshot, ocr_result, button_name)
            if not is_valid:
                print("❌ LLM não validou a região")
                return False
            print("✓ LLM confirmou o botão")

        self.last_found_coords = ocr_result
        return True
    
    def list_items_below(self, parent_name):
        """Lista todos os itens abaixo de um item pai usando LLM + OCR"""
        print(f"🔍 Listando itens abaixo de '{parent_name}'...")

        screenshot = self.capture_screen()
        screenshot.save('temp_list.png')

        # LLM identifica quais itens estão abaixo
        prompt = f"""Nesta imagem, quais itens estão abaixo de '{parent_name}'? 
        Liste apenas os nomes dos itens, um por linha, sem numeração ou símbolos."""

        response = ollama.chat(
            model=self.llm_model,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': ['temp_list.png']
            }]
        )

        items_text = response['message']['content'].strip()
        items_list = [item.strip() for item in items_text.split('\n') if item.strip()]

        print(f"✓ LLM encontrou {len(items_list)} itens: {items_list}")

        # OCR extrai coordenadas de cada item
        img_array = np.array(screenshot)
        ocr_results = self.ocr_reader.readtext(img_array)

        items_dict = {}
        for item_name in items_list:
            for (bbox, text, confidence) in ocr_results:
                if item_name.lower() in text.lower() and confidence > 0.5:
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    center_x = int(sum(x_coords) / 4)
                    center_y = int(sum(y_coords) / 4)

                    items_dict[item_name] = {
                        'x': center_x,
                        'y': center_y
                    }
                    break

        print(f"✓ Coordenadas extraídas: {items_dict}")
        return items_dict
    def find_all_with_template(self, screenshot, template_path, threshold=0.7):
        """
        Encontra TODOS os matches de um template na screenshot.
        Retorna uma lista com as coordenadas de todos os matches encontrados.
        """
        try:
            # Carrega a imagem e o template
            if isinstance(screenshot, str):
                img = cv2.imread(screenshot)
            else:
                img = np.array(screenshot)

            template = cv2.imread(template_path)

            if img is None or template is None:
                print(f"❌ Erro ao carregar imagem ou template")
                return {'found': False, 'matches': []}

            # Converte pra escala de cinza
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # Template matching
            result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

            # Encontra todos os matches acima do threshold
            locations = np.where(result >= threshold)

            if len(locations[0]) == 0:
                print(f"❌ Nenhum match encontrado")
                return {'found': False, 'matches': []}

            # Agrupa matches próximos (evita duplicatas)
            h, w = template_gray.shape
            matches = []

            for pt in zip(*locations[::-1]):
                x, y = pt
                confidence = result[y, x]

                # Verifica se já existe um match muito próximo
                is_duplicate = False
                for existing_match in matches:
                    distance = np.sqrt((x - existing_match['x'])**2 + (y - existing_match['y'])**2)
                    if distance < w / 2:  # Se está muito perto, é duplicata
                        is_duplicate = True
                        break

                if not is_duplicate:
                    matches.append({
                        'x': x + w // 2,  # Centro da bolinha
                        'y': y + h // 2,
                        'confidence': float(confidence)
                    })

            # Ordena por confiança (maior primeiro)
            matches.sort(key=lambda m: m['confidence'], reverse=True)

            print(f"✓ Encontrados {len(matches)} matches")
            for i, match in enumerate(matches):
                print(f"  Match {i+1}: ({match['x']}, {match['y']}) - Confiança: {match['confidence']:.2%}")

            return {'found': True, 'matches': matches}

        except Exception as e:
            print(f"❌ Erro em find_all_with_template: {e}")
            return {'found': False, 'matches': []}

