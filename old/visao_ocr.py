# visaoOCR.py
import cv2
import numpy as np
import easyocr
import pyautogui
import pygetwindow as gw
import time

# Inicializa OCR apenas uma vez (rápido e eficiente)
reader = easyocr.Reader(['en'])


# --------------------------------------------------------
#  CAPTURA DA JANELA - SEMPRE SALVA completo.png
# --------------------------------------------------------
def capturar_janela(titulo_janela="SCENE"):
    """Captura screenshot da janela e salva completo.png."""
    
    janelas = gw.getWindowsWithTitle(titulo_janela)
    if not janelas:
        print(f"[ERRO] Janela '{titulo_janela}' não encontrada.")
        return None, None

    janela = janelas[0]

    try:
        janela.activate()
        janela.maximize()
        time.sleep(0.7)
    except:
        pass

    x, y = janela.left, janela.top
    w, h = janela.width, janela.height

    # Captura screenshot apenas da janela
    screenshot = pyautogui.screenshot(region=(x, y, w, h))
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Salva para debug
    cv2.imwrite("completo.png", screenshot)

    return screenshot, janela



# --------------------------------------------------------
#  OCR - Encontrar apenas um botão
# --------------------------------------------------------
def vocrBtn(texto_procurado):
    """
    Retorna a posição absoluta do botão que contenha o texto.
    Se vários existirem, retorna o primeiro.
    """
    screenshot, janela = capturar_janela("SCENE")
    if screenshot is None:
        return None

    resultados = reader.readtext(screenshot)

    alvo = texto_procurado.lower().replace(" ", "")

    for bbox, texto, conf in resultados:
        txt = texto.lower().replace(" ", "")
        if alvo in txt:
            (x1, y1), (x2, y2), _, _ = bbox
            centro_x = janela.left + int((x1 + x2) / 2)
            centro_y = janela.top + int((y1 + y2) / 2)
            return (centro_x, centro_y)

    return None



# --------------------------------------------------------
#  OCR - Encontrar vários botões
# --------------------------------------------------------
def vocrBtns(texto_procurado):
    """
    Retorna uma lista com TODAS as posições absolutas 
    de botões que contenham o texto passado.
    """
    screenshot, janela = capturar_janela("SCENE")
    if screenshot is None:
        return []

    resultados = reader.readtext(screenshot)

    alvo = texto_procurado.lower().replace(" ", "")
    botoes = []

    for bbox, texto, conf in resultados:
        txt = texto.lower().replace(" ", "")
        if alvo in txt:
            (x1, y1), (x2, y2), _, _ = bbox
            centro_x = janela.left + int((x1 + x2) / 2)
            centro_y = janela.top + int((y1 + y2) / 2)
            botoes.append((centro_x, centro_y))

    return botoes
