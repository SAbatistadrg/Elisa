# ocr_analyzer.py
import easyocr
from pathlib import Path
import re

class OCRAnalyzer:
    def __init__(self):
        print("🔄 Carregando EasyOCR (pode demorar na primeira vez)...")
        self.reader = easyocr.Reader(['en'], gpu=True)
        print("✓ EasyOCR carregado")

    def extract_slider_value(self, image_path):
        """Extrai o valor numérico do slider"""
        try:
            print(f"   → Lendo imagem com EasyOCR...")

            results = self.reader.readtext(str(image_path))

            print(f"   → Encontrados {len(results)} texto(s)")

            # Salva TODOS os textos encontrados
            all_texts = []
            for (bbox, text, confidence) in results:
                print(f"      • '{text}' (confiança: {confidence:.2f})")
                all_texts.append(f"{text} (conf: {confidence:.2f})")

            # Retorna o texto completo encontrado
            full_text = " | ".join(all_texts) if all_texts else "N/A"

            # Tenta extrair número
            for (bbox, text, confidence) in results:
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    value = float(numbers[0])
                    print(f"   ✓ Valor extraído: {value}")
                    return value, full_text

            print(f"   ⚠️  Nenhum número encontrado")
            return "N/A", full_text

        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return "ERROR", f"ERROR: {str(e)}"

    def _extract_number_from_filename(self, filename):
        """Extrai o número do nome do arquivo pos-templateX.png"""
        match = re.search(r'pos-template(\d+)', filename.stem)
        return int(match.group(1)) if match else 0

    def analyze_all_crops(self, crops_dir="./salvos"):
        """Analisa todos os recortes pos-template e salva em txt"""
        crops_dir = Path(crops_dir)
        crop_files = list(crops_dir.glob("pos-template*.png"))

        if not crop_files:
            print("❌ Nenhum recorte encontrado")
            return []

        crop_files = sorted(crop_files, key=self._extract_number_from_filename)

        print(f"\n🔍 Analisando {len(crop_files)} recorte(s) com EasyOCR...")
        print("=" * 60)

        values = []
        txt_content = []
        txt_content.append("=" * 60)
        txt_content.append("ANÁLISE OCR - RESULTADOS")
        txt_content.append("=" * 60)
        txt_content.append("")

        for idx, crop_file in enumerate(crop_files, 1):
            print(f"\n📊 [{idx}/{len(crop_files)}] {crop_file.name}")
            value, full_text = self.extract_slider_value(crop_file)
            values.append(value)

            # Adiciona ao txt
            txt_content.append(f"[{idx}] {crop_file.name}")
            txt_content.append(f"    Valor extraído: {value}")
            txt_content.append(f"    Textos encontrados: {full_text}")
            txt_content.append("")

        # Salva o arquivo txt
        txt_path = crops_dir / "analise.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(txt_content))

        print(f"\n💾 Análise salva em: {txt_path}")

        return values
