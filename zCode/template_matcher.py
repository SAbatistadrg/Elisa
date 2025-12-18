# template_matcher.py
import cv2
import numpy as np
from pathlib import Path

class TemplateMatcher:
    def __init__(self, template_paths, threshold=0.8, offset_width=50, offset_height=50):
        """
        template_paths: dict com {nome: caminho} dos templates
        """
        self.templates = {}
        self.threshold = threshold
        self.offset_width = offset_width
        self.offset_height = offset_height

        print(f"🔍 Carregando {len(template_paths)} template(s)...")

        for name, path in template_paths.items():
            template_path = Path(path)
            if not template_path.exists():
                print(f"   ⚠️  Template não encontrado: {name} ({path})")
                continue

            template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            h, w = template_gray.shape

            self.templates[name] = {
                'image': template,
                'gray': template_gray,
                'width': w,
                'height': h,
                'path': template_path
            }

            print(f"   ✓ {name}: {w}x{h}px")

        print(f"✓ {len(self.templates)} template(s) carregado(s)")
        print(f"  Offset: largura +{self.offset_width}px, altura +{self.offset_height}px")

    def _non_maximum_suppression(self, matches, overlap_threshold=0.7):
        """Remove matches duplicados que se sobrepõem"""
        if len(matches) == 0:
            return []

        matches = sorted(matches, key=lambda x: x['confidence'], reverse=True)

        keep = []

        for match in matches:
            x1, y1 = match['x'], match['y']
            x2, y2 = x1 + match['width'], y1 + match['height']

            overlap = False

            for kept_match in keep:
                kx1, ky1 = kept_match['x'], kept_match['y']
                kx2, ky2 = kx1 + kept_match['width'], ky1 + kept_match['height']

                # Distância entre centros
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                kept_center_x = (kx1 + kx2) / 2
                kept_center_y = (ky1 + ky2) / 2

                distance = ((center_x - kept_center_x)**2 + (center_y - kept_center_y)**2)**0.5

                if distance < 30:
                    overlap = True
                    break

                # Calcula interseção
                ix1 = max(x1, kx1)
                iy1 = max(y1, ky1)
                ix2 = min(x2, kx2)
                iy2 = min(y2, ky2)

                if ix1 < ix2 and iy1 < iy2:
                    intersection = (ix2 - ix1) * (iy2 - iy1)
                    area1 = (x2 - x1) * (y2 - y1)
                    area2 = (kx2 - kx1) * (ky2 - ky1)

                    iou = intersection / min(area1, area2)

                    if iou > overlap_threshold:
                        overlap = True
                        break

            if not overlap:
                keep.append(match)

        return keep

    def find_matches_in_image(self, image_path):
        """Encontra todas as ocorrências de TODOS os templates em uma imagem"""
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        all_matches = []

        for template_name, template_data in self.templates.items():
            template_gray = template_data['gray']

            result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)

            locations = np.where(result >= self.threshold)

            for pt in zip(*locations[::-1]):
                confidence = result[pt[1], pt[0]]

                all_matches.append({
                    'template': template_name,
                    'x': int(pt[0]),
                    'y': int(pt[1]),
                    'width': template_data['width'],
                    'height': template_data['height'],
                    'confidence': float(confidence)
                })

        unique_matches = self._non_maximum_suppression(all_matches, overlap_threshold=0.7)

        return unique_matches

    def search_in_screenshots(self, screenshot_paths, save_dir="./salvos"):
        """Busca templates em múltiplos screenshots e salva recortes"""
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)

        all_results = []
        all_crops = []
        crop_counter = 1

        for screenshot_path in screenshot_paths:
            print(f"\n📸 Analisando: {screenshot_path.name}")

            matches = self.find_matches_in_image(screenshot_path)

            if matches:
                # ORDENA DE CIMA PRA BAIXO
                matches = sorted(matches, key=lambda m: m['y'])

                print(f"   ✓ Encontrados {len(matches)} input(s)")

                image = cv2.imread(str(screenshot_path))

                for match in matches:
                    template_name = match['template']
                    x, y = match['x'], match['y']
                    w, h = match['width'], match['height']
                    confidence = match['confidence']

                    print(f"      • {template_name} em ({x}, {y}) - confiança: {confidence:.2f}")

                    x1 = max(0, x - self.offset_width)
                    y1 = max(0, y - self.offset_height)
                    x2 = min(image.shape[1], x + w + self.offset_width)
                    y2 = min(image.shape[0], y + h + self.offset_height)

                    crop = image[y1:y2, x1:x2]

                    crop_filename = f"pos-template{crop_counter}.png"
                    crop_path = save_dir / crop_filename
                    cv2.imwrite(str(crop_path), crop)

                    all_crops.append(crop_path)
                    crop_counter += 1

                    match['crop_path'] = crop_path
                    match['screenshot'] = screenshot_path.name

                all_results.extend(matches)
            else:
                print(f"   ⚠️  Nenhum input encontrado")

        total_found = len(all_results)

        print(f"\n{'='*60}")
        print(f"Total geral: {total_found} input(s) encontrado(s)")
        print(f"Recortes salvos: {len(all_crops)}")

        return total_found, all_results, all_crops
