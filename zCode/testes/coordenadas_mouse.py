import pyautogui
import time

print("Movimente o mouse para ver as coordenadas em tempo real")
print("Pressione Ctrl+C para sair\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"X: {x:4d} Y: {y:4d}", end='\r')
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nScript finalizado!")
