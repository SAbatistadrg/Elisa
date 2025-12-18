# main.py
from zCode.tools.capture_module import PageCapture
from template_matcher import TemplateMatcher
from zCode.ocr_analyzer_for_sliders import OCRAnalyzer
from notifications import notify

def main():
    notify("Iniciando detecção de inputs", "🎬 Scene Automation")

    print("=" * 60)
    print("🎬 INICIANDO DETECÇÃO DE INPUTS COM TEMPLATE MATCHING")
    print("=" * 60)

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

    capturer.click_to_activate()

    print("\n" + "=" * 60)
    print("📸 CAPTURANDO SCREENSHOTS INICIAIS")
    print("=" * 60)

    notify("Capturando screenshots...", "📸 Scene Automation")
    screenshots = capturer.capture_initial_screenshots()

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

if __name__ == "__main__":
    main()
