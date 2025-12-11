# llm_analyzer.py
import ollama
from pathlib import Path
import base64

class LLMAnalyzer:
    def __init__(self, model="llava:13b"):
        self.model = model
        print(f"✓ LLM Analyzer inicializado com modelo: {self.model}")

    def encode_image(self, image_path):
        """Converte imagem para base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def extract_slider_value(self, image_path):
        """Extrai o valor do slider usando LLM com visão"""
        image_b64 = self.encode_image(image_path)

        prompt = """Look at this image of a slider control.
Extract ONLY the numeric value shown below the slider.
Return just the number, nothing else.
Example: if you see "0.150", return: 0.150"""

        try:
            print(f"   → Enviando para {self.model}...")
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_b64]
                }]
            )

            value = response['message']['content'].strip()
            print(f"   → Resposta do modelo: {value}")

            # Tenta limpar a resposta e converter pra float
            try:
                # Remove texto extra e pega só números
                import re
                numbers = re.findall(r'\d+\.?\d*', value)
                if numbers:
                    numeric_value = float(numbers[0])
                    return numeric_value
                else:
                    return value
            except:
                return value

        except Exception as e:
            print(f"   ❌ Erro ao analisar {image_path.name}: {e}")
            return "ERROR"

    def analyze_all_crops(self, crops_dir="./salvos"):
        """Analisa todos os recortes pos-template na pasta"""
        crops_dir = Path(crops_dir)
        crop_files = sorted(crops_dir.glob("pos-template*.png"))

        if not crop_files:
            print("❌ Nenhum recorte pos-template encontrado")
            return []

        print(f"\n🤖 Analisando {len(crop_files)} recorte(s) com {self.model}...")
        print("=" * 60)

        values = []

        for idx, crop_file in enumerate(crop_files, 1):
            print(f"\n📊 [{idx}/{len(crop_files)}] Analisando: {crop_file.name}")
            value = self.extract_slider_value(crop_file)
            values.append(value)
            print(f"   ✓ Valor final: {value}")

        return values
