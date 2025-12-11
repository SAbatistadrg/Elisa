# capture_module.py
import pyautogui
import time
from pathlib import Path
import win32gui
import win32con

class PageCapture:
    def __init__(self, save_dir="./salvos"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

    def clear_saved_images(self):
        """Limpa a pasta de salvos antes de cada execução"""
        for file in self.save_dir.glob("*.png"):
            file.unlink()
        print(f"✓ Pasta {self.save_dir} limpa")

    def activate_scene_window(self):
        """Ativa e maximiza a janela do Scene"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "scene" in title.lower():
                    windows.append((hwnd, title))
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if not windows:
            print("❌ Janela do Scene não encontrada")
            return False

        hwnd, title = windows[0]
        print(f"✓ Janela encontrada: {title}")

        # Ativa a janela
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        # Maximiza
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        time.sleep(0.5)

        return True

    def click_to_activate(self):
        """Dá um clique na página para ativá-la"""
        screen_width, screen_height = pyautogui.size()
        # Clica no centro da tela
        pyautogui.click(screen_width // 2, screen_height // 2)
        time.sleep(0.3)
        print("✓ Clique de ativação realizado")

    def capture_initial_screenshots(self):
        """Captura os dois prints iniciais"""
        screenshots = []

        # Pressiona Home
        pyautogui.press('home')
        time.sleep(0.5)
        print("✓ Home pressionado")

        # Primeiro print
        screenshot1 = pyautogui.screenshot()
        path1 = self.save_dir / "pre-template1.png"
        screenshot1.save(path1)
        screenshots.append(path1)
        print(f"✓ Screenshot 1 salvo: {path1}")

        # Pressiona PgDn
        pyautogui.press('pagedown')
        time.sleep(0.5)
        print("✓ PageDown pressionado")

        # Segundo print
        screenshot2 = pyautogui.screenshot()
        path2 = self.save_dir / "pre-template2.png"
        screenshot2.save(path2)
        screenshots.append(path2)
        print(f"✓ Screenshot 2 salvo: {path2}")

        return screenshots
