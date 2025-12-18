# movimento.py
import pyautogui

def moverPara(x, y, duracao=0.2):
    pyautogui.moveTo(x, y, duration=duracao)

def click():
    pyautogui.click()
    