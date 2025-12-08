# 🔍 ANÁLISIS DEL PROBLEMA - HOLD NO SE EXPIRA

## 🎯 PROBLEMA IDENTIFICADO

**Síntoma:**
- Usuario 1: Crea PRE-RESERVA (HOLD con 600 segundos = 10 minutos)
- Usuario 2: Ve que habitación está NO DISPONIBLE ✅
- **PERO:** Después de 10+ minutos, la habitación SIGUE bloqueada ❌

---

## 🔎 ANÁLISIS DE LOS SPs

### ¿Cómo funciona la expiración en tu SQL?

**En `sp_expirarHoldsVencidos`:**

```sql
-- Busca HOLD/RESERVA donde:
WHERE H.ESTADO_HOLD = 1                                    -- HOLD está activo
  AND R.ESTADO_GENERAL_RESERVA = 'PRE-RESERVA'            -- Es pre-reserva
  AND ISNULL(R.ESTADO_RESERVA, 1) = 1                      -- No está cancelada
  AND DATEADD(SECOND, H.TIEMPO_HOLD, R.FECHA_REGISTRO_RESERVA) <= @NOW;
      -- FECHA_REGISTRO + TIEMPO_HOLD (segundos) <= AHORA
```

**ESTO SIGNIFICA:**
```
EJEMPLO:
- FECHA_REGISTRO_RESERVA = 2025-12-06 11:00:00
- TIEMPO_HOLD = 600 segundos (10 minutos)
- CALCULO: 11:00:00 + 600 seg = 11:10:00

¿Expira si?
- AHORA >= 11:10:01 ✅ SÍ
- AHORA = 11:10:00 ✅ SÍ (el = es importante)
- AHORA = 11:09:59 ❌ NO (todavía no)
```

---

## ⚠️ EL PROBLEMA REAL

**El SP `sp_expirarHoldsVencidos` EXISTE en SQL Server, pero:**

### ❌ El middleware de Django NO está expirando los HOLDs

**Razón:** Django no sabe que debe ejecutar `sp_expirarHoldsVencidos` automáticamente

---

## 🔗 FLUJO ACTUAL (INCOMPLETO)

```
TIMELINE:
T = 0 seg → Usuario crea PRE-RESERVA
  ├─ sp_crearPreReserva_1_1_usuario_interno ejecuta:
  │  └─ EXEC dbo.sp_expirarHoldsVencidos  ← Expira OTROS HOLDs vencidos
  ├─ Crea HOLD con ESTADO_HOLD = 1
  └─ Habitación BLOQUEADA

T = 600 seg → HOLD DEBERÍA expirar pero NADIE lo ejecuta ❌

T = 610 seg → Usuario 2 intenta crear PRE-RESERVA
  └─ sp_crearPreReserva_1_1_usuario_interno ejecuta:
     └─ EXEC dbo.sp_expirarHoldsVencidos  ← AQUÍ sí expira el HOLD anterior ✅
     
T = 615 seg → Ahora SÍ la habitación está disponible ✅
```

**EL PROBLEMA:**
- La expiración SOLO ocurre cuando alguien intenta crear una NUEVA pre-reserva
- Si NADIE crea pre-reservas nuevas, los HOLDs viejos NUNCA se expiran
- La habitación queda bloqueada indefinidamente ❌

---

## ✅ LA SOLUCIÓN

### Opción 1: RECOMENDADA - Llamar desde Django ANTES de validar disponibilidad

**En Django (antes de buscar habitaciones disponibles):**

```python
# views.py - En HabitacionesAjaxView.get()
def get(self, request):
    try:
        # 🔑 PRIMERO: Expirar HOLDs vencidos
        from servicios.rest.gestion.HoldGestionRest import HoldGestionRest
        api_hold = HoldGestionRest()
        
        try:
            resultado = api_hold.expirar_holds_vencidos()
            print(f"[DEBUG] HOLDs expirados: {resultado}")
        except Exception as e:
            print(f"[WARN] Error al expirar HOLDs (continuamos anyway): {e}")
        
        # SEGUNDO: Continuar con búsqueda de habitaciones
        # ... resto del código ...
```

### Opción 2: ALTERNATIVA - Ejecutar en background cada X segundos

**Ya está implementada en el middleware que creamos:**

```python
# En settings.py
MIDDLEWARE = [
    ...
    'webapp.middleware_hold.ExpirarHoldsMiddleware',  # ← Ejecuta automáticamente
]
```

### Opción 3: RECOMENDADA TAMBIÉN - Llamar antes de buscar

```python
# services/hold_service.py (NUEVO ARCHIVO)

def asegurar_holds_expirados():
    """
    Ejecuta la expiración de HOLDs en background.
    Se debe llamar ANTES de cualquier operación de búsqueda de habitaciones.
    """
    from servicios.rest.gestion.HoldGestionRest import HoldGestionRest
    from threading import Thread
    
    def expirar():
        try:
            api_hold = HoldGestionRest()
            api_hold.expirar_holds_vencidos()
        except Exception as e:
            print(f"[WARN] Error al expirar HOLDs: {e}")
    
    # Ejecutar en background sin bloquear
    thread = Thread(target=expirar, daemon=True)
    thread.start()
```

---

## 🎯 RECOMENDACIÓN: IMPLEMENTAR INMEDIATAMENTE

### Paso 1: Crear archivo de servicio

**Crear:** `servicios/hold_service.py`

```python
from servicios.rest.gestion.HoldGestionRest import HoldGestionRest
from threading import Thread
import time


def expirar_holds_vencidos_background():
    """Ejecuta la expiración de HOLDs sin bloquear"""
    try:
        print("[HOLD_SERVICE] Expirando HOLDs vencidos...")
        api_hold = HoldGestionRest()
        resultado = api_hold.expirar_holds_vencidos()
        print(f"[HOLD_SERVICE] ✓ Resultado: {resultado}")
        return resultado
    except Exception as e:
        print(f"[HOLD_SERVICE ERROR] {e}")
        return None


def expirar_holds_async():
    """
    Lanza expiración en thread daemon (no bloquea).
    Se debe llamar ANTES de operaciones críticas:
    - Buscar habitaciones
    - Crear pre-reserva
    - Validar disponibilidad
    """
    thread = Thread(target=expirar_holds_vencidos_background, daemon=True)
    thread.start()


def expirar_holds_sync():
    """
    Expiración sincrónica (bloquea hasta completar).
    Usar solo cuando sea crítico garantizar que se complete.
    """
    return expirar_holds_vencidos_background()
```

### Paso 2: Llamar en vistas críticas

**En `webapp/views.py`, en la función `HabitacionesAjaxView.get()`:**

```python
class HabitacionesAjaxView(View):
    def get(self, request):
        try:
            # ✅ PRIMERO: Asegurar que HOLDs vencidos se expiren
            from servicios.hold_service import expirar_holds_async
            expirar_holds_async()  # En background
            
            # El resto del código sigue normalmente
            # ...
```

### Paso 3: También en detalle de habitación

```python
def detalle_habitacion(request, id):
    """Detalle de habitación específica"""
    # ✅ Expirar HOLDs antes de mostrar disponibilidad
    from servicios.hold_service import expirar_holds_async
    expirar_holds_async()
    
    # ... resto del código ...
```

### Paso 4: También en endpoint de fechas ocupadas

```python
@method_decorator(csrf_exempt, name="dispatch")
class FechasOcupadasAjaxView(View):
    def get(self, request, id_habitacion):
        try:
            # ✅ Expirar HOLDs vencidos primero
            from servicios.hold_service import expirar_holds_async
            expirar_holds_async()
            
            # ... resto del código ...
```

---

## 📊 RESULTADO DESPUÉS DE IMPLEMENTAR

```
TIMELINE MEJORADO:

T = 0 seg → Usuario 1 crea PRE-RESERVA
  └─ HOLD creado, ESTADO = 1
  └─ Habitación BLOQUEADA

T = 60 seg → Usuario 2 busca habitaciones
  ├─ expirar_holds_async() se ejecuta en background
  ├─ sp_expirarHoldsVencidos se ejecuta
  └─ ❌ HOLD NO expira aún (solo 60 seg de 600)

T = 605 seg → Usuario 3 busca habitaciones
  ├─ expirar_holds_async() se ejecuta
  ├─ sp_expirarHoldsVencidos se ejecuta
  ├─ ✅ HOLD EXPIRA (605 >= 600)
  ├─ RESERVA marcada como EXPIRADO
  ├─ HOLD marcada como INACTIVO
  └─ ✅ Habitación DISPONIBLE nuevamente

T = 610 seg → Usuario 2 ve habitación disponible ✅
```

---

## 🛡️ VENTAJAS DE ESTA SOLUCIÓN

✅ **Simple:** Una línea de código en cada vista crítica
✅ **No bloquea:** Ejecuta en background con threads daemon
✅ **Automático:** Se ejecuta cada vez que alguien busca
✅ **Garantizado:** El SP ya valida la lógica en SQL
✅ **Sin cambios en C#:** Usa el endpoint que ya existe

---

## 🔧 IMPLEMENTACIÓN PASO A PASO

### 1. Crear `servicios/hold_service.py` ✅
### 2. En `HabitacionesAjaxView.get()`: Agregar `expirar_holds_async()`
### 3. En `detalle_habitacion()`: Agregar `expirar_holds_async()`
### 4. En `FechasOcupadasAjaxView.get()`: Agregar `expirar_holds_async()`
### 5. Opcionalmente: Agregar middleware a settings.py para redundancia

---

## ⚡ CÓDIGO PARA COPIAR-PEGAR

```python
# Agregar esto al INICIO de cada función que busque/valide habitaciones:

from servicios.hold_service import expirar_holds_async
expirar_holds_async()  # Se ejecuta sin bloquear
```

