"""
middleware_hold.py
Middleware para ejecutar automáticamente la expiración de HOLDs
"""

import time
import threading
from django.utils.deprecation import MiddlewareNotUsed
from servicios.rest.gestion.HoldGestionRest import HoldGestionRest


class ExpirarHoldsMiddleware:
    """
    Middleware que expira automáticamente los HOLDs vencidos
    cada X segundos (sin bloquear las vistas).
    
    Configuración en settings.py:
    MIDDLEWARE = [
        ...
        'webapp.middleware_hold.ExpirarHoldsMiddleware',
    ]
    
    # Intervalo en segundos (por defecto 60)
    HOLD_EXPIRATION_INTERVAL = 60
    """
    
    # Clase para compartir estado entre requests
    class _Estado:
        ultimo_chequeo = 0
        interval = 60  # Segundos entre chequeos
        lock = threading.Lock()
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Intentar expirar HOLDs si pasó el intervalo
        self._chequear_expirar_holds()
        
        # Procesar request normalmente
        response = self.get_response(request)
        return response
    
    @classmethod
    def _chequear_expirar_holds(cls):
        """
        Verifica si es tiempo de expirar HOLDs y lo hace en background.
        No bloquea el request.
        """
        ahora = time.time()
        
        with cls._Estado.lock:
            if (ahora - cls._Estado.ultimo_chequeo) < cls._Estado.interval:
                # No es tiempo todavía
                return
            
            # Actualizar tiempo del último chequeo
            cls._Estado.ultimo_chequeo = ahora
        
        # Ejecutar expiración en background (no bloquea)
        thread = threading.Thread(
            target=cls._expirar_holds_background,
            daemon=True
        )
        thread.start()
    
    @staticmethod
    def _expirar_holds_background():
        """Ejecuta la expiración de HOLDs en background"""
        try:
            api_hold = HoldGestionRest()
            resultado = api_hold.expirar_holds_vencidos()
            print(f"[MIDDLEWARE] ✓ HOLDs expirados automáticamente: {resultado}")
        except Exception as e:
            print(f"[MIDDLEWARE ERROR] Error al expirar HOLDs: {e}")


class MonitorearHoldsMiddleware:
    """
    Middleware alternativo que monitorea HOLDs pero no expira automáticamente.
    Solo registra información en logs.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_hold = HoldGestionRest()
    
    def __call__(self, request):
        # Solo si es una vista de reservas
        if '/reservas/' in request.path or '/pagos/' in request.path:
            self._monitorear_holds()
        
        response = self.get_response(request)
        return response
    
    def _monitorear_holds(self):
        """Monitorea el estado de los HOLDs"""
        try:
            holds_activos = self.api_hold.obtener_holds_activos()
            
            for hold in holds_activos[:3]:  # Solo los primeros 3
                segundos_restantes = self.api_hold.tiempo_hold_restante(hold)
                print(f"[MONITOR HOLD] {hold.get('IdHold')}: {segundos_restantes}s restantes")
        except Exception as e:
            # Fallar silenciosamente para no impactar los requests
            pass
