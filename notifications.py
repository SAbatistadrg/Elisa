# notifications.py

from win10toast import ToastNotifier

def notify(message, title="Notificação", duration=5):
    """
    Envia notificação do Windows

    Args:
        message (str): Mensagem da notificação
        title (str): Título (padrão: "Notificação")
        duration (int): Duração em segundos (padrão: 5)
    """
    try:
        toaster = ToastNotifier()
        toaster.show_toast(
            title=title,
            msg=message,
            duration=duration,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Erro ao enviar notificação: {e}")
