# movimento.py
import pyautogui

def moverPara(x, y, duracao=0.2):
    pyautogui.moveTo(x, y, duration=duracao)

def click():
    pyautogui.click()
    
def enter():
    pyautogui.press('enter')

def press(key, presses=1, interval=0.1):
    pyautogui.press(key, presses=presses, interval=interval)