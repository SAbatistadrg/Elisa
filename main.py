# main.py
from button_locator import ButtonLocator
from window_manager import activate_and_maximize_scene_window
from capture_module import PageCapture
from template_matcher import TemplateMatcher
from ocr_analyzer import OCRAnalyzer
from notifications import notify
import time
import pyautogui
import os
from moves import click, moverPara
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

    # Verifica se já está na opção correta (matching parcial)
    if "vista superior" in current_option and "nuvem" in current_option:
        print(f"✅ Opção correta já está selecionada!")
        notify("Opção correta!", title="Elisa", duration=2)
        pyautogui.press('return')
        time.sleep(1)
        return True

    # Encontra quantas setas são necessárias (matching parcial)
    matched = False
    arrows_needed = 0

    for option_name, arrow_count in options_map.items():
        # Extrai palavras-chave principais (primeiras 2 palavras)
        keywords = option_name.split()[:2]
        if all(keyword in current_option for keyword in keywords):
            arrows_needed = arrow_count
            matched = True
            break

    if not matched:
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

def registro_automatico_flow():
    """Fluxo de registro automático e seleção de clusters"""
    print("\n" + "=" * 60)
    print("🎯 INICIANDO FLUXO DE REGISTRO AUTOMÁTICO")
    print("=" * 60)

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

def deteccao_inputs_flow():
    """Fluxo de detecção de inputs com OCR"""
    print("\n" + "=" * 60)
    print("🔍 INICIANDO FLUXO DE DETECÇÃO DE INPUTS")
    print("=" * 60)

    notify("Iniciando detecção de inputs", "🎬 Scene Automation")

    WIDTH_OFFSET = 50
    HEIGHT_OFFSET = 50

    TEMPLATES = {
        'slidebar': r'C:\dev\opencv-button-identifier\buttons\input_slidebar.png',
        'slidebar_empty': r'C:\dev\opencv-button-identifier\buttons\input_slidebar_empty.png'
    }

    capturer = PageCapture(save_dir="./salvos")
    capturer.clear_saved_images()

    print("\n" + "=" * 60)
    print("🪟 ATIVANDO JANELA DO SCENE")
    print("=" * 60)

    if not capturer.activate_scene_window():
        notify("❌ Não foi possível ativar a janela do Scene", "Erro", duration=10)
        print("❌ Não foi possível ativar a janela do Scene")
        return

    # Clica na janela e pressiona Home
    capturer.click_to_activate()
    time.sleep(0.5)
    print("⬆️ Pressionando Home para ir ao topo...")
    pyautogui.press('home')
    time.sleep(1)

    print("\n" + "=" * 60)
    print("📸 CAPTURANDO SCREENSHOTS INICIAIS")
    print("=" * 60)
    notify("Capturando screenshots...", "📸 Scene Automation")

    # Captura primeiro print (após Home)
    screenshots = capturer.capture_initial_screenshots()

    # Pressiona PgDn e captura segundo print
    print("⬇️ Pressionando PgDn para próxima página...")
    pyautogui.press('pagedown')
    time.sleep(1)

    # Captura segundo print (após PgDn)
    screenshots.extend(capturer.capture_initial_screenshots())

    print("\n" + "=" * 60)
    print("🔍 INICIANDO TEMPLATE MATCHING")
    print("=" * 60)
    notify("Buscando inputs na página...", "🔍 Scene Automation")

    matcher = TemplateMatcher(
        template_paths=TEMPLATES,
        threshold=0.8,
        offset_width=WIDTH_OFFSET,
        offset_height=HEIGHT_OFFSET
    )

    total_found, results, crops = matcher.search_in_screenshots(
        screenshots, 
        save_dir="./salvos"
    )

    print("\n" + "=" * 60)
    print("📊 RESULTADO DO TEMPLATE MATCHING")
    print("=" * 60)
    print(f"Total de inputs encontrados: {total_found}")
    print(f"Total de recortes salvos: {len(crops)}")

    if results:
        template_counts = {}
        for result in results:
            template_name = result['template']
            template_counts[template_name] = template_counts.get(template_name, 0) + 1

        print("\nBreakdown por template:")
        for template_name, count in template_counts.items():
            print(f"  • {template_name}: {count}")

        notify(f"✓ {total_found} input(s) encontrado(s)", "📊 Template Matching")

    if total_found > 0:
        print("\n" + "=" * 60)
        print("🔍 INICIANDO ANÁLISE COM EASYOCR")
        print("=" * 60)
        notify("Extraindo valores com OCR...", "🔍 Scene Automation")

        analyzer = OCRAnalyzer()
        values = analyzer.analyze_all_crops(crops_dir="./salvos")

        print("\n" + "=" * 60)
        print("📋 VALORES DETECTADOS")
        print("=" * 60)
        print(f"Lista de valores: {values}")
        print("=" * 60)

        # Notificação final com os valores
        values_str = ", ".join([str(v) for v in values])
        notify(f"✅ Valores extraídos: {values_str}", "📋 Concluído", duration=10)
    else:
        notify("⚠️ Nenhum input encontrado", "Scene Automation", duration=10)
        print("\n⚠️  Nenhum input encontrado para analisar")

def main():
    """Main unificado - executa os dois fluxos em sequência"""
    print("\n" + "=" * 80)
    print("🚀 AUTOMAÇÃO COMPLETA DO SCENE")
    print("=" * 80)

    # Fluxo 1: Registro automático e seleção de clusters
    registro_automatico_flow()

    print("\n" + "=" * 80)
    print("⏭️  PASSANDO PARA O PRÓXIMO FLUXO...")
    print("=" * 80)
    time.sleep(2)

    # Fluxo 2: Detecção de inputs com OCR
    deteccao_inputs_flow()

    print("\n" + "=" * 80)
    print("✅ AUTOMAÇÃO COMPLETA FINALIZADA!")
    print("=" * 80)
    notify("✅ Automação completa finalizada!", "🎉 Scene Automation", duration=5)

if __name__ == "__main__":
    main()
