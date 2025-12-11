import ollama

MODEL = "bahtiyorovnozim/qwen3-vl-1-4b"
IMAGE_PATH = "C:/dev/opencv-button-identifier/images/completo.png"


# 1) Subamostra - seção "Baseado em Exibição Superior"
def vllmSBES() -> str:
    prompt = (
        "Retorne apenas os valores de subsampling / subamostras para a seção 'Baseado em Exibição Superior'. "
        "Formato EXATO: 0.4 — e nada mais. Caso nao encontre, retorne None"
    )

    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [IMAGE_PATH]
        }]
    )
    return response["message"]["content"].strip()


# 2) Confiabilidade (Reliability)
def vllmConfiabilidade() -> str:
    prompt = (
        "Retorne apenas os valores de reliability / confiabilidade. "
        "Formato EXATO: 0.4 — e nada mais. Caso nao encontre, retorne None"
    )

    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [IMAGE_PATH]
        }]
    )
    return response["message"]["content"].strip()


# 3) Subamostra - seção "Nuvem para Nuvem"
def vllmSNPN() -> str:
    prompt = (
        "Retorne apenas os valores de subsampling para a seção 'Nuvem para Nuvem'. "
        "Formato EXATO: 0.4 - e nada mais. Caso nao encontre, retorne None"
    )

    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [IMAGE_PATH]
        }]
    )
    return response["message"]["content"].strip()


# 4) Função genérica — prompt customizado
def vllmGenerico(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [IMAGE_PATH]
        }]
    )
    return response["message"]["content"].strip()

#here
def vllmLoc(botao: str, image_path="completo.png") -> tuple:
    """
    Versão melhorada com verificações e normalização.
    """
    from PIL import Image
    
    # Carrega imagem para pegar dimensões reais
    img = Image.open(image_path)
    largura, altura = img.size
    
    prompt = f"""Analise esta imagem de {largura}x{altura} pixels.

Localize o elemento: "{botao}"

Retorne APENAS as coordenadas X,Y do centro em pixels absolutos.
Formato obrigatório: X,Y
Exemplo: 450,320

Não explique. Apenas os números."""

    response = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [image_path]
        }]
    )

    texto = response["message"]["content"].strip()
    
    # Remove possível texto extra
    import re
    match = re.search(r'(\d+)\s*,\s*(\d+)', texto)
    
    if not match:
        raise ValueError(f"Resposta inesperada: {texto}")
    
    x, y = int(match.group(1)), int(match.group(2))
    
    # Validação básica
    if x > largura or y > altura or x < 0 or y < 0:
        print(f"⚠️ Coordenadas suspeitas: ({x},{y}) para imagem {largura}x{altura}")
    
    return x, y


if __name__ == "__main__":
    print(vllmSBES())
    print(vllmConfiabilidade())
    print(vllmSNPN())
    print(vllmGenerico("Retorne o percentual de pixels brancos na imagem."))