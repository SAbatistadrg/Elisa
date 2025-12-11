import os
import time
import pyautogui
from button_locator import ButtonLocator
from window_manager import activate_and_maximize_scene_window
from moves import click, moverPara
from notifications import notify

def main_test_balls():
    """Main temporário pra testar identificação e movimento das bolinhas"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    locator = ButtonLocator()

    # Ativa e maximiza a janela do Scene
    activate_and_maximize_scene_window()
    time.sleep(2)

    # Captura a tela
    screenshot = locator.capture_screen()
    screenshot.save('temp_test_balls.png')

    # Procura por todas as bolinhas
    template_path = os.path.join(script_dir, "buttons", "ball_input.png")

    if not os.path.exists(template_path):
        print(f"❌ Template não encontrado: {template_path}")
        return

    result = locator.find_all_with_template('temp_test_balls.png', template_path, threshold=0.7)

    if not result['found'] or len(result['matches']) < 2:
        print("❌ Não foram encontradas 2 bolinhas")
        return

    # ===== PRIMEIRA BOLINHA (Subamostra) =====
    first_ball = result['matches'][0]
    print(f"\n🔵 Clicando na PRIMEIRA bolinha (Subamostra) em: ({first_ball['x']}, {first_ball['y']})")
    notify(f"Clicando bolinha 1 - Subamostra", title="Elisa", duration=2)
    moverPara(first_ball['x'], first_ball['y'])
    click()
    time.sleep(0.5)

    # Anda 5x pra direita
    print("➡️ Andando 5x pra DIREITA...")
    for i in range(5):
        pyautogui.press('right')
        time.sleep(0.2)

    time.sleep(1)

    # ===== SEGUNDA BOLINHA (Confiabilidade) =====
    second_ball = result['matches'][1]
    print(f"\n🔵 Clicando na SEGUNDA bolinha (Confiabilidade) em: ({second_ball['x']}, {second_ball['y']})")
    notify(f"Clicando bolinha 2 - Confiabilidade", title="Elisa", duration=2)
    moverPara(second_ball['x'], second_ball['y'])
    click()
    time.sleep(0.5)

    # Anda 5x pra esquerda
    print("⬅️ Andando 5x pra ESQUERDA...")
    for i in range(5):
        pyautogui.press('left')
        time.sleep(0.2)

    time.sleep(1)

    # ===== SCROLL 500 PIXELS =====
    print("🖱️ Scrollando 500 pixels pra baixo...")
    notify("Scrollando 500px...", title="Elisa", duration=2)
    pyautogui.scroll(-5000)  # -5 unidades = ~600 pixels pra baixo

    time.sleep(1)

    # ===== PROCURA NOVAMENTE A BOLINHA =====
    print("🔍 Procurando bolinhas novamente...")
    screenshot = locator.capture_screen()
    screenshot.save('temp_test_balls_after_scroll.png')

    result = locator.find_all_with_template('temp_test_balls_after_scroll.png', template_path, threshold=0.7)

    if not result['found'] or len(result['matches']) < 1:
        print("❌ Bolinha não encontrada após scroll")
        return

    # ===== CLICA NA BOLINHA E ANDA 10x PRA DIREITA =====
    ball_after_scroll = result['matches'][0]
    print(f"\n🔵 Clicando na bolinha após scroll em: ({ball_after_scroll['x']}, {ball_after_scroll['y']})")
    notify(f"Clicando bolinha após scroll", title="Elisa", duration=2)
    moverPara(ball_after_scroll['x'], ball_after_scroll['y'])
    click()
    time.sleep(0.5)

    print("➡️ Andando 10x pra DIREITA...")
    for i in range(10):
        pyautogui.press('right')
        time.sleep(0.2)

    print("\n✅ Teste concluído!")
    notify("Teste finalizado!", title="Elisa", duration=2)

if __name__ == "__main__":
    main_test_balls()
