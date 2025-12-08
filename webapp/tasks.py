"""
tasks.py
Tareas asincrónicas para Django (puede usar Celery o Threading simple)
"""

import threading
import time
from django.core.management.base import BaseCommand
from servicios.rest.gestion.HoldGestionRest import HoldGestionRest


def expirar_holds_vencidos_background():
    """
    Expira HOLDs vencidos de forma asincrónica sin bloquear las vistas.
    Puede ejecutarse como:
    - Thread en segundo plano
    - Tarea Celery
    - Cron job
    """
    try:
        print("[TASK] Iniciando expiración de HOLDs vencidos...")
        api_hold = HoldGestionRest()
        resultado = api_hold.expirar_holds_vencidos()
        print(f"[TASK] ✓ Expiración completada: {resultado}")
        return resultado
    except Exception as e:
        print(f"[ERROR TASK] Error al expirar HOLDs: {e}")
        return {"error": str(e)}


def expirar_holds_async():
    """
    Ejecuta la expiración de HOLDs en un thread daemon.
    No bloquea la ejecución principal.
    """
    thread = threading.Thread(target=expirar_holds_vencidos_background, daemon=True)
    thread.start()
    print("[TASK] Expiración de HOLDs iniciada en background")


def expirar_holds_sync():
    """
    Ejecuta la expiración de HOLDs de forma sincrónica (bloqueante).
    Más seguro para garantizar que se completa antes de continuar.
    """
    return expirar_holds_vencidos_background()


# ============================================================
# COMANDO DE DJANGO (para ejecutar manualmente)
# ============================================================
class Command(BaseCommand):
    help = 'Expira los HOLDs vencidos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando expiración de HOLDs...'))
        
        try:
            resultado = expirar_holds_vencidos_background()
            self.stdout.write(self.style.SUCCESS(f'✓ {resultado}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {e}'))


# ============================================================
# CONFIGURACIÓN PARA CELERY (OPCIONAL)
# ============================================================
# Si tienes Celery configurado, usa esto en lugar de los anteriores:
# 
# from celery import shared_task
# 
# @shared_task
# def task_expirar_holds_vencidos():
#     """Tarea Celery para expirar HOLDs"""
#     return expirar_holds_vencidos_background()
#
#
# # En settings.py, agregar:
# CELERY_BEAT_SCHEDULE = {
#     'expirar-holds-vencidos': {
#         'task': 'webapp.tasks.task_expirar_holds_vencidos',
#         'schedule': timedelta(seconds=60),  # Cada 60 segundos
#     },
# }
