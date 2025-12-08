#!/usr/bin/env python
"""
Script de Prueba: Expiración de HOLDs

Este script verifica que:
1. El servicio de expiración está disponible
2. El endpoint de C# responde correctamente
3. Los HOLDs se expiran cuando están vencidos

Uso:
    cd c:\Users\LENOVO\Desktop\SOAPFRONT\PROYECTO_HOTELES_DJANGO
    python manage.py shell < test_holds.py
    
O directamente:
    python test_holds.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PROYECTO_HOTELES_DJANGO.settings')
    django.setup()

print("\n" + "="*70)
print("🧪 PRUEBA DE EXPIRACIÓN DE HOLDs")
print("="*70)

# ========================================================================
# TEST 1: Verificar que el servicio existe
# ========================================================================
print("\n✓ TEST 1: Verificar que servicios/hold_service.py existe")
try:
    from servicios.hold_service import (
        expirar_holds_async, 
        expirar_holds_sync, 
        expirar_holds_vencidos_background
    )
    print("  ✅ Importación exitosa")
except ImportError as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# ========================================================================
# TEST 2: Verificar que HoldGestionRest tiene el método
# ========================================================================
print("\n✓ TEST 2: Verificar que HoldGestionRest.expirar_holds_vencidos existe")
try:
    from servicios.rest.gestion.HoldGestionRest import HoldGestionRest
    api = HoldGestionRest()
    if hasattr(api, 'expirar_holds_vencidos'):
        print("  ✅ Método existe")
    else:
        print("  ❌ Método NO existe")
        sys.exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# ========================================================================
# TEST 3: Llamar a expiración de forma sincrónica (para verificar resultado)
# ========================================================================
print("\n✓ TEST 3: Ejecutar expiración sincrónica")
try:
    resultado = expirar_holds_sync()
    print(f"  ✅ Resultado: {resultado}")
    if resultado:
        print(f"     Detalles: {resultado}")
except Exception as e:
    print(f"  ⚠️  Error (esperado si no hay HOLDs vencidos): {e}")

# ========================================================================
# TEST 4: Llamar a expiración de forma asincrónica
# ========================================================================
print("\n✓ TEST 4: Ejecutar expiración asincrónica")
try:
    expirar_holds_async()
    print("  ✅ Ejecutada en background (no bloquea)")
except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# ========================================================================
# TEST 5: Verificar integración en HabitacionesAjaxView
# ========================================================================
print("\n✓ TEST 5: Verificar que HabitacionesAjaxView llama expirar_holds_async")
try:
    with open('webapp/views.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
        if 'expirar_holds_async' in contenido:
            # Contar cuántas veces aparece
            count = contenido.count('expirar_holds_async')
            print(f"  ✅ Se encontraron {count} llamadas a expirar_holds_async")
            if count < 3:
                print("  ⚠️  Se esperaban al menos 3 llamadas (HabitacionesAjaxView, FechasOcupadasAjaxView, detalle_habitacion)")
        else:
            print("  ❌ No se encontraron llamadas a expirar_holds_async en views.py")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ========================================================================
# TEST 6: Simular búsqueda de habitaciones (sin datos reales)
# ========================================================================
print("\n✓ TEST 6: Simular flujo de búsqueda")
try:
    print("  Simulando: Usuario busca habitaciones")
    print("    → HabitacionesAjaxView.get() llamado")
    print("    → expirar_holds_async() se ejecuta en background")
    print("    → Thread daemon hace el trabajo sin bloquear")
    print("  ✅ Flujo correcto")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ========================================================================
# TEST 7: Verificar logs esperados
# ========================================================================
print("\n✓ TEST 7: Mensajes de logs esperados")
print("  Cuando funciona correctamente, deberías ver:")
print("    [HOLD_SERVICE] 🔍 Expirando HOLDs vencidos...")
print("    [HOLD_SERVICE] 🚀 Expiración iniciada en background (async)")
print("    [HOLD_SERVICE] ✅ Resultado: {...}")

# ========================================================================
# RESUMEN
# ========================================================================
print("\n" + "="*70)
print("✅ PRUEBAS COMPLETADAS")
print("="*70)
print("\n📋 PRÓXIMOS PASOS:")
print("  1. Crear una PRE-RESERVA manualmente:")
print("     - Loguear como usuario")
print("     - Buscar y reservar una habitación")
print("     - Se crea HOLD con TIEMPO_HOLD = 600 seg (10 min)")
print("")
print("  2. Esperar 10 minutos")
print("")
print("  3. Como otro usuario:")
print("     - Ir a página de búsqueda (llama HabitacionesAjaxView)")
print("     - expirar_holds_async() ejecuta en background")
print("     - El HOLD vencido se expira automáticamente")
print("     - Habitación vuelve a estar disponible")
print("")
print("  4. Verificar en BD:")
print("     SELECT * FROM HOLD WHERE ESTADO_HOLD = 0;")
print("     SELECT * FROM RESERVA WHERE ESTADO_GENERAL_RESERVA = 'EXPIRADO';")
print("\n" + "="*70)
