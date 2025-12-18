from plyer import notification
ativado = True

def notify(message, title="Scene Automation", duration=5):
    
    if ativado == True:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Scene Automation",
                timeout=duration
            )
        except Exception as e:
            print(f"⚠️ Notificação falhou: {e}")
    else:
        pass