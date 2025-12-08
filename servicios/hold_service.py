"""
Servicio para gestionar la expiración de HOLDs.

Los HOLDs se crean con un tiempo límite (TIEMPO_HOLD en segundos).
Si no se confirma la pre-reserva en ese tiempo, el HOLD vence y la 
habitación vuelve a estar disponible.

Este servicio asegura que se ejecute sp_expirarHoldsVencidos 
ANTES de cualquier operación crítica (búsqueda de habitaciones, validación, etc.)
"""

from servicios.rest.gestion.HoldGestionRest import HoldGestionRest
from threading import Thread
import time
import logging

logger = logging.getLogger(__name__)


def expirar_holds_vencidos_background():
    """
    Ejecuta la expiración de HOLDs vencidos.
    Llamada al SP: sp_expirarHoldsVencidos
    
    La lógica SQL:
    - Busca HOLD con ESTADO_HOLD = 1 (activos)
    - Valida que RESERVA.ESTADO_GENERAL_RESERVA = 'PRE-RESERVA'
    - Verifica: DATEADD(SECOND, TIEMPO_HOLD, FECHA_REGISTRO) <= AHORA
    - Si cumple: marca HOLD.ESTADO_HOLD = 0 y RESERVA.ESTADO = 'EXPIRADO'
    """
    try:
        print("[HOLD_SERVICE] 🔍 Expirando HOLDs vencidos...")
        logger.info("[HOLD_SERVICE] Expirando HOLDs vencidos...")
        
        api_hold = HoldGestionRest()
        resultado = api_hold.expirar_holds_vencidos()
        
        print(f"[HOLD_SERVICE] ✅ Resultado: {resultado}")
        logger.info(f"[HOLD_SERVICE] ✅ Resultado: {resultado}")
        
        return resultado
        
    except Exception as e:
        print(f"[HOLD_SERVICE] ❌ Error: {e}")
        logger.error(f"[HOLD_SERVICE] Error al expirar HOLDs: {e}")
        return None


def expirar_holds_async():
    """
    Ejecuta la expiración de HOLDs en thread daemon (NO BLOQUEA).
    
    Ideal para llamar ANTES de:
    - Buscar habitaciones disponibles
    - Crear pre-reserva
    - Validar disponibilidad de fechas
    
    Ejemplo de uso:
        from servicios.hold_service import expirar_holds_async
        expirar_holds_async()  # Inicia en background
        # El código continúa sin esperar
    """
    thread = Thread(target=expirar_holds_vencidos_background, daemon=True)
    thread.start()
    print("[HOLD_SERVICE] 🚀 Expiración iniciada en background (async)")


def expirar_holds_sync():
    """
    Ejecuta la expiración de HOLDs de forma sincrónica (BLOQUEA).
    
    Usar SOLO cuando sea crítico garantizar que la expiración se complete
    ANTES de continuar. Normalmente no es necesario.
    
    Ejemplo de uso:
        from servicios.hold_service import expirar_holds_sync
        resultado = expirar_holds_sync()  # Espera a que termine
        if resultado:
            print("HOLDs expirados")
    """
    print("[HOLD_SERVICE] ⏳ Expiración sincrónica (bloqueante)...")
    return expirar_holds_vencidos_background()
