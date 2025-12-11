# window_manager.py

import pyautogui
import pygetwindow as gw
import time

def activate_and_maximize_scene_window():
    """Encontra, ativa e maximiza a janela com 'SCENE' no título"""
    try:
        # Procura pela janela com "SCENE" no título
        scene_windows = [w for w in gw.getAllWindows() if "SCENE" in w.title.upper()]

        if not scene_windows:
            print("❌ Nenhuma janela com 'SCENE' encontrada")
            return False

        window = scene_windows[0]

        # Ativa a janela
        window.activate()
        time.sleep(0.5)

        # Maximiza
        window.maximize()
        time.sleep(0.5)

        print(f"✅ Janela '{window.title}' ativada e maximizada")
        return True

    except Exception as e:
        print(f"❌ Erro ao ativar janela: {e}")
        return False
