# main.py
from tools.capture_module import PageCapture
from template_matcher import TemplateMatcher
from ocr_analyzer_for_sliders import OCRAnalyzer
import os

def callOCRSliders():
    # Pega o diretório do script (zCode/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Sobe um nível para Elisa/ (raiz do projeto)
    project_root = os.path.dirname(script_dir)

    WIDTH_OFFSET = 50
    HEIGHT_OFFSET = 50

    TEMPLATES = {
        'slidebar': os.path.join(project_root, 'buttons', 'input_slidebar.png'),
        'slidebar_empty': os.path.join(project_root, 'buttons', 'input_slidebar_empty.png')
    }

    capturer = PageCapture(save_dir="./salvos")
    capturer.clear_saved_images()

    capturer.click_to_activate()
    screenshots = capturer.capture_initial_screenshots()

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

    if total_found > 0:
        analyzer = OCRAnalyzer()
        values = analyzer.analyze_all_crops(crops_dir="./salvos")
        return values

    return []

if __name__ == "__main__":
    callOCRSliders()
