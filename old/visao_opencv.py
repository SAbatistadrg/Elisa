# visao.py
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
from capturar_janela import capturar_janela


def localizar_botao(template_path, titulo_janela="SCENE", threshold=0.8):
    """Localiza um único template (melhor match)."""
    
    screenshot, janela = capturar_janela(titulo_janela)
    if screenshot is None:
        return None

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"[ERRO] Template '{template_path}' não encontrado!")
        return None

    h, w = template.shape[:2]

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        return None

    x, y = max_loc

    centro_x = janela.left + x + w // 2
    centro_y = janela.top + y + h // 2

    return (centro_x, centro_y)


# -------------------------------------------------------------
#   🔥 NOVA FUNÇÃO: localizar TODOS os botões iguais
# -------------------------------------------------------------
def localizar_botoes(template_path, titulo_janela="SCENE", threshold=0.8):
    time.sleep(3)
    """
    Localiza TODOS os matches do template e retorna
    uma lista de coordenadas absolutas do centro de cada botão.
    """
    
    screenshot, janela = capturar_janela(titulo_janela)
    if screenshot is None:
        return []

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"[ERRO] Template '{template_path}' não encontrado!")
        return []

    h, w = template.shape[:2]

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

    # encontra TODOS os pontos acima do limiar
    y_locs, x_locs = np.where(result >= threshold)

    botoes = []

    for (x, y) in zip(x_locs, y_locs):
        centro_x = janela.left + x + w // 2
        centro_y = janela.top + y + h // 2
        botoes.append((centro_x, centro_y))

    return botoes
