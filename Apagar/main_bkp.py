from button_locator import ButtonLocator
from window_manager import activate_and_maximize_scene_window
import time
import pyautogui
import os
from moves import click, moverPara
from notifications import notify
import ollama

def verify_and_select_dropdown(locator, script_dir):
    """
    1. Testa os 4 templates pra abrir o dropdown (qualquer um é válido)
    2. Tira print e pergunta pra IA oq está selecionado em azul
    3. IA retorna a opção selecionada
    4. Baseado na resposta, digita setas pra baixo + ENTER
    """
    time.sleep(2)

    # Passo 1: Testa os 4 templates pra abrir o dropdown
    templates = [
        "vista_superior_e_nuvem_a_nuvem.png",
        "com_base_no_alvo.png",
        "com_base_na_vista_superior.png",
        "nuvem_a_nuvem.png"
    ]

    dropdown_opened = False

    for template_name in templates:
        template_path = os.path.join(script_dir, "buttons", template_name)

        if not os.path.exists(template_path):
            print(f"⚠️ Template não encontrado: {template_name}")
            continue

        print(f"🔍 Testando template: {template_name}")
        screenshot = locator.capture_screen()
        result = locator.find_with_template(screenshot, template_path)

        if result['found']:
            print(f"✓ Template '{template_name}' encontrado em: ({result['x']}, {result['y']})")
            moverPara(result['x'], result['y'])
            click()
            dropdown_opened = True
            time.sleep(1)
            break

    if not dropdown_opened:
        print("❌ Nenhum template foi encontrado")
        notify("Erro ao abrir dropdown", title="Elisa", duration=3)
        return False

    # Passo 2: Tira print do dropdown aberto
    time.sleep(0.5)
    screenshot = locator.capture_screen()
    screenshot.save('temp_dropdown_check.png')

    # Passo 3: Pergunta pra IA oq está selecionado em azul
    prompt = "Qual é a opção que está selecionada/destacada em AZUL neste dropdown? Responda APENAS com o nome exato da opção, nada mais."

    response = ollama.chat(
        model=locator.llm_model,
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': ['temp_dropdown_check.png']
        }]
    )

    current_option = response['message']['content'].strip().lower()
    print(f"🤖 IA detectou opção selecionada: {current_option}")
    notify(f"Opção atual: {current_option}", title="Elisa", duration=2)

    # Mapeamento de opções e quantas setas pra baixo são necessárias
    options_map = {
        "com base no alvo": 3,
        "com base na vista superior": 2,
        "nuvem a nuvem": 1,
        "vista superior e nuvem a nuvem": 0
    }

    # Passo 4: Baseado na resposta, digita setas pra baixo + ENTER
    target_option = "vista superior e nuvem a nuvem"

    if target_option in current_option:
        print(f"✅ Opção correta já está selecionada!")
        notify("Opção correta!", title="Elisa", duration=2)
        pyautogui.press('return')
        time.sleep(1)
        return True

    # Encontra quantas setas são necessárias
    arrows_needed = 0
    for option_name, arrow_count in options_map.items():
        if option_name in current_option:
            arrows_needed = arrow_count
            break

    if arrows_needed == 0 and target_option not in current_option:
        print("❌ Opção não reconhecida")
        notify("Erro ao identificar opção", title="Elisa", duration=3)
        return False

    print(f"⬇️ Pressionando seta pra baixo {arrows_needed}x...")

    # Digita as setas pra baixo
    for i in range(arrows_needed):
        pyautogui.press('down')
        time.sleep(0.2)

    # Pressiona ENTER
    time.sleep(0.3)
    pyautogui.press('return')
    time.sleep(1)

    print(f"✅ Opção 'Vista superior e Nuvem a Nuvem' selecionada!")
    notify("Opção selecionada!", title="Elisa", duration=2)
    return True





def main():
    # Ativa e maximiza a janela SCENE
    activate_and_maximize_scene_window()
    locator = ButtonLocator(llm_model="bahtiyorovnozim/qwen3-vl-1-4b")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        template_path = os.path.join(script_dir, "buttons", "registro_automatico.png")
        use_template = template_path if os.path.exists(template_path) else None
        result = locator.locate_tm(
            button_name="",
            use_template=use_template,
            validate_llm=False
        )
        notify(f"{result['found'],result['x'],result['y']}", title="Elisa", duration=3)
        moverPara(result['x'],result['y'])
        click()
        time.sleep(3)
    except:
        notify("Ocorreu um erro inesperado", title="Elisa", duration=5)
    # Escaneia os clusters
    try:
        notify("Iniciando identificação de clusters...", title="Elisa", duration=3)
        clusters = locator.list_items_below("Scans")
        notify("Escaneado com sucesso!", title="Elisa", duration=3)
        # Clica nos clusters encontrados
        for nome, coords in clusters.items():
            moverPara(coords['x'], coords['y'])
            click()
            # Clica em "Selecionar método"            
            try:
                template_path = os.path.join(script_dir, "buttons", "selecionar_metodo.png")
                use_template = template_path if os.path.exists(template_path) else None
                success = locator.locate_tm(
                    button_name="Selecionar método",
                    use_template=use_template,
                    validate_llm=True
                )
                if success:
                    found_coords = locator.last_found_coords
                    print(f"\n✅ Botão encontrado em: ({found_coords['x']}, {found_coords['y']})")
                    # Clique manual aqui
                    moverPara(found_coords['x'], found_coords['y'])
                    click()

                    # ============ INICIO - VERIFICAR E SELECIONAR DROPDOWN ============
                    verify_and_select_dropdown(locator, script_dir)
                    # ============ FIM - VERIFICAR E SELECIONAR DROPDOWN ============
                    input("here")

                else:
                    found_coords = locator.last_ocr_coords
                    print("\n❌ Não foi possível localizar o botão.")
            except Exception as e:
                print(f"❌ Erro: {e}")
                import traceback
                traceback.print_exc()
                found_coords = locator.last_ocr_coords
            if found_coords:
                pyautogui.moveTo(found_coords['x'], found_coords['y'], duration=0.5)
    except:
        input("Falha no sistema de identificação de clusters, aperte ENTER para continuar...")

if __name__ == "__main__":
    main()
