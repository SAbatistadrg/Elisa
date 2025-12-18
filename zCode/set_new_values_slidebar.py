import os
import time
import pyautogui
from button_locator import ButtonLocator
from simple.window_manager import activate_and_maximize_scene_window
from simple.moves import click, moverPara
from simple.notifications import notify
from callOCRSliders import callOCRSliders

# Passos de cada slider
SLIDER_STEPS = [0.005, 0.05, 0.001]  # input1, input2, input3

def adjust_sliders_to_target(target_values):
    """
    Ajusta os sliders pros valores desejados
    target_values: lista com 3 valores [input1, input2, input3]
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    template_path = os.path.join(project_root, 'buttons', 'ball_input.png')

    if not os.path.exists(template_path):
        print(f"❌ Template não encontrado: {template_path}")
        return

    locator = ButtonLocator()

    # Pega valores atuais
    current_values = callOCRSliders()

    if len(current_values) != 3 or len(target_values) != 3:
        print("❌ Erro: precisa de exatamente 3 valores")
        return

    print(f"\n🎯 Ajustando sliders:")
    print(f"   Atual: {current_values}")
    print(f"   Alvo:  {target_values}")

    # Clica no canto superior esquerdo pra ativar
    print("\n🖱️ Ativando janela...")
    #pyautogui.click(1182, 743)
    time.sleep(0.3)

    # ===== SLIDERS 1 e 2 (após Home) =====
    print("\n🏠 Apertando Home...")
    pyautogui.press('home')
    time.sleep(1)

    # Procura bolinhas 1 e 2
    screenshot = locator.capture_screen()
    screenshot.save('temp_adjust_sliders.png')
    result = locator.find_all_with_template('temp_adjust_sliders.png', template_path, threshold=0.7)

    if result['found'] and len(result['matches']) >= 2:
        # SLIDER 1 (primeira bolinha após Home)
        slider_idx = 0
        current = current_values[slider_idx]
        target = target_values[slider_idx]
        step = SLIDER_STEPS[slider_idx]

        if current != "N/A" and current != "ERROR":
            diff = target - current
            steps_needed = int(round(diff / step))

            if steps_needed != 0:
                direction = 'right' if steps_needed > 0 else 'left'
                steps_abs = abs(steps_needed)

                print(f"\n🔧 Slider 1: {current} → {target}")
                print(f"   Precisa: {steps_abs} passos pra {direction}")

                ball = result['matches'][0]  # Primeira bolinha
                print(f"   🔵 Clicando em ({ball['x']}, {ball['y']})")
                notify(f"Ajustando slider 1", title="Elisa", duration=2)
                moverPara(ball['x'], ball['y'])
                click()
                time.sleep(0.3)

                print(f"   ⌨️  Pressionando '{direction}' {steps_abs}x...")
                for _ in range(steps_abs):
                    pyautogui.press(direction)
                    time.sleep(0.05)
                time.sleep(0.5)
            else:
                print(f"\n✓ Slider 1: já está no valor correto ({current})")

        # SLIDER 2 (segunda bolinha após Home)
        slider_idx = 1
        current = current_values[slider_idx]
        target = target_values[slider_idx]
        step = SLIDER_STEPS[slider_idx]

        if current != "N/A" and current != "ERROR":
            diff = target - current
            steps_needed = int(round(diff / step))

            if steps_needed != 0:
                direction = 'right' if steps_needed > 0 else 'left'
                steps_abs = abs(steps_needed)

                print(f"\n🔧 Slider 2: {current} → {target}")
                print(f"   Precisa: {steps_abs} passos pra {direction}")

                ball = result['matches'][1]  # Segunda bolinha
                print(f"   🔵 Clicando em ({ball['x']}, {ball['y']})")
                notify(f"Ajustando slider 2", title="Elisa", duration=2)
                moverPara(ball['x'], ball['y'])
                click()
                time.sleep(0.3)

                print(f"   ⌨️  Pressionando '{direction}' {steps_abs}x...")
                for _ in range(steps_abs):
                    pyautogui.press(direction)
                    time.sleep(0.05)
                time.sleep(0.5)
            else:
                print(f"\n✓ Slider 2: já está no valor correto ({current})")
    else:
        print("   ❌ Bolinhas 1 e 2 não encontradas após Home")

    # ===== SLIDER 3 (após End) =====
    print("\n📜 Apertando End...")
    moverPara(1182, 743)
    click()
    pyautogui.press('end')
    time.sleep(1)

    # Procura bolinha 3
    screenshot = locator.capture_screen()
    screenshot.save('temp_adjust_sliders.png')
    result = locator.find_all_with_template('temp_adjust_sliders.png', template_path, threshold=0.7)

    if result['found'] and len(result['matches']) > 0:
        slider_idx = 2
        current = current_values[slider_idx]
        target = target_values[slider_idx]
        step = SLIDER_STEPS[slider_idx]

        if current != "N/A" and current != "ERROR":
            diff = target - current
            steps_needed = int(round(diff / step))

            if steps_needed != 0:
                direction = 'right' if steps_needed > 0 else 'left'
                steps_abs = abs(steps_needed)

                print(f"\n🔧 Slider 3: {current} → {target}")
                print(f"   Precisa: {steps_abs} passos pra {direction}")

                ball = result['matches'][0]  # Primeira (e única) bolinha
                print(f"   🔵 Clicando em ({ball['x']}, {ball['y']})")
                notify(f"Ajustando slider 3", title="Elisa", duration=2)
                moverPara(ball['x'], ball['y'])
                click()
                time.sleep(0.3)

                print(f"   ⌨️  Pressionando '{direction}' {steps_abs}x...")
                for _ in range(steps_abs):
                    pyautogui.press(direction)
                    time.sleep(0.05)
                time.sleep(0.5)
            else:
                print(f"\n✓ Slider 3: já está no valor correto ({current})")
    else:
        print("   ❌ Bolinha 3 não encontrada após End")

    print("\n✅ Ajuste concluído!")
    notify("Sliders ajustados!", title="Elisa", duration=2)

    # Verifica valores finais
    print("\n🔍 Verificando valores finais...")
    final_values = callOCRSliders()
    print(f"📊 Valores finais: {final_values}")

if __name__ == "__main__":
    activate_and_maximize_scene_window()
    time.sleep(2)
    target = [0.05, 0.4, 0.03]
    adjust_sliders_to_target(target)
