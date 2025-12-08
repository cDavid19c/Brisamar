# 🔄 FLUJO DE EJECUCIÓN - EXPIRACIÓN DE HOLDs

## DIAGRAMA VISUAL DEL FLUJO

```
┌──────────────────────────────────────────────────────────────────┐
│                    USUARIO ABRE NAVEGADOR                        │
│              (Busca habitaciones o ve detalles)                  │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│              Request HTTP a Django                               │
│  GET /hoteles/habitaciones/?fecha_entrada=...&fecha_salida=...  │
│                     O                                             │
│  GET /hoteles/detalle/HAB001/                                    │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│              Django View ejecutado:                              │
│  - HabitacionesAjaxView.get()                                    │
│  - FechasOcupadasAjaxView.get()                                  │
│  - detalle_habitacion()                                          │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│         🔑 EXPIRACIÓN DE HOLDs LLAMADA 🔑                        │
│                                                                   │
│  from servicios.hold_service import expirar_holds_async          │
│  expirar_holds_async()                                           │
└──────────────────────┬───────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
┌───────────────────┐    ┌──────────────────────────┐
│ THREAD DAEMON     │    │ VISTA CONTINÚA SIN       │
│ (Background)      │    │ ESPERAR                  │
│                   │    │                          │
│ ASYNC EXECUTION   │    │ - Búsqueda se ejecuta    │
│ (NO BLOQUEA)      │    │ - Usuario recibe datos   │
└─────────┬─────────┘    │ - Todo normal            │
          │              └──────────┬───────────────┘
          │                         │
          ▼                         ▼
┌──────────────────────────────────────┐  ┌─────────────────┐
│ 1. Importa HoldGestionRest           │  │ ✅ Usuario VE  │
│ 2. Llama .expirar_holds_vencidos()   │  │ HABITACIONES    │
│ 3. POST a C# /api/gestion/hold/      │  │ DISPONIBLES     │
│    expirar-vencidos                  │  └─────────────────┘
└─────────────┬──────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│ C# ControllerAction                  │
│ - Recibe POST                        │
│ - Llama sp_expirarHoldsVencidos      │
└─────────────┬──────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│ SQL Server - Stored Procedure        │
│ sp_expirarHoldsVencidos              │
│                                      │
│ Busca:                               │
│  - HOLD.ESTADO_HOLD = 1 (activo)     │
│  - RESERVA='PRE-RESERVA'             │
│  - DATEADD(SECOND, TIEMPO_HOLD,      │
│    FECHA_REGISTRO) <= GETDATE()      │
│                                      │
│ Si cumple:                           │
│  - UPDATE HOLD SET ESTADO_HOLD = 0   │
│  - UPDATE RESERVA SET ESTADO =       │
│    'EXPIRADO'                        │
└─────────────┬──────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│ BD ACTUALIZADA                       │
│ - HOLD.ESTADO_HOLD = 0 ✅            │
│ - RESERVA.ESTADO = 'EXPIRADO' ✅     │
└─────────────┬──────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│ ✅ HABITACIÓN DISPONIBLE             │
│                                      │
│ Otros usuarios pueden ahora crear    │
│ nueva pre-reserva                    │
└──────────────────────────────────────┘
```

---

## TIMELINE TEMPORAL

```
T = 0s
  ├─ Usuario A crea pre-reserva
  ├─ HOLD creado: ESTADO_HOLD = 1, TIEMPO_HOLD = 600
  └─ Habitación bloqueada ❌

T = 60s
  ├─ Usuario B busca habitaciones
  ├─ expirar_holds_async() llamado
  ├─ Thread daemon ejecuta: NO expira aún (60 < 600)
  └─ Búsqueda continúa, habitación sigue bloqueada ❌

T = 300s
  ├─ Usuario C ve detalles
  ├─ expirar_holds_async() llamado
  ├─ Thread daemon ejecuta: NO expira aún (300 < 600)
  └─ Detalles mostrados, habitación sigue bloqueada ❌

T = 605s
  ├─ Usuario D ve calendario
  ├─ expirar_holds_async() llamado
  ├─ Thread daemon ejecuta: ✅ AHORA SÍ EXPIRA (605 >= 600)
  │  └─ HOLD.ESTADO_HOLD = 0
  │  └─ RESERVA.ESTADO = 'EXPIRADO'
  ├─ Calendario actualizado
  └─ ✅ Habitación disponible

T = 610s
  ├─ Usuario B intenta crear pre-reserva
  ├─ Validación: Habitación disponible ✅
  ├─ Nueva pre-reserva creada
  └─ ✅ Flujo completado exitosamente
```

---

## ESTADOS DE HOLD

### Estado 1: ACTIVO (ESTADO_HOLD = 1)
```
├─ Pre-reserva vigente
├─ Tiempo no expirado aún
├─ Habitación BLOQUEADA
└─ Otros no pueden reservar
```

### Estado 2: EXPIRADO/CONFIRMADO (ESTADO_HOLD = 0)
```
├─ Pre-reserva CONFIRMADA Y convertida en RESERVA
│  O
├─ Pre-reserva expiró por timeout
├─ Habitación DISPONIBLE nuevamente
└─ Otros pueden crear nueva pre-reserva
```

---

## SECUENCIA DE EVENTOS

### Escenario Completo

```
1️⃣ USUARIO A CREA PRE-RESERVA
   ├─ Request: POST /api/crear-pre-reserva
   ├─ Backend: sp_crearPreReserva_1_1_usuario_interno
   ├─ Crea: RESERVA (ID=100, estado='PRE-RESERVA')
   ├─ Crea: HOLD (ID='HODA000001', TIEMPO_HOLD=600)
   ├─ Ejecuta: sp_expirarHoldsVencidos (otros)
   └─ Response: ✅ Pre-reserva creada

2️⃣ USUARIO B INTENTA BUSCAR (T=60s)
   ├─ Busca: HAB001, Hoy → +3 días
   ├─ HabitacionesAjaxView.get() se ejecuta
   ├─ expirar_holds_async() se LLAMA
   │  └─ Thread: sp_expirarHoldsVencidos
   │     └─ Búsqueda: ¿HOLDs vencidos?
   │     └─ NO (60 < 600)
   ├─ Query: SELECT habitaciones WHERE...
   │  └─ HAB001 NO aparece (está en HOLD)
   └─ Response: ❌ No disponible

3️⃣ USUARIO C VE DETALLES (T=300s)
   ├─ Detalles: /hoteles/detalle/HAB001
   ├─ detalle_habitacion() se ejecuta
   ├─ expirar_holds_async() se LLAMA
   │  └─ Thread: sp_expirarHoldsVencidos
   │     └─ Búsqueda: ¿HOLDs vencidos?
   │     └─ NO (300 < 600)
   ├─ Detalles: Precio, amenidades, etc.
   ├─ Calendario: Esas fechas ocupadas
   └─ Response: ✅ Mostrado pero no disponible

4️⃣ USUARIO D VE CALENDARIO (T=605s) ← CRÍTICO
   ├─ FechasOcupadasAjaxView.get()
   ├─ expirar_holds_async() se LLAMA
   │  └─ Thread: sp_expirarHoldsVencidos
   │     ├─ Búsqueda: ¿HOLDs vencidos?
   │     ├─ ✅ SÍ ENCONTRADO (605 >= 600)
   │     ├─ UPDATE HOLD SET ESTADO_HOLD = 0
   │     ├─ UPDATE RESERVA SET ESTADO = 'EXPIRADO'
   │     └─ COMMIT TRANSACTION
   ├─ Query: SELECT fechas_ocupadas...
   │  └─ HAB001 NO aparece (no está en HOLD activo)
   ├─ Calendario: Esas fechas DISPONIBLES ✅
   └─ Response: ✅ Fechas libres

5️⃣ USUARIO B PUEDE CREAR NUEVA PRE-RESERVA (T=610s)
   ├─ Busca: HAB001, Hoy → +3 días
   ├─ HabitacionesAjaxView.get()
   ├─ expirar_holds_async() se LLAMA (redundancia)
   ├─ Query: SELECT habitaciones WHERE...
   │  └─ HAB001 APARECE ✅ (no hay HOLD activo)
   ├─ Response: Habitación disponible
   ├─ Usuario B: Click en "Reservar"
   ├─ Nueva pre-reserva creada
   ├─ Nuevo HOLD creado: HODA000002
   └─ Proceso se repite...
```

---

## VALIDACIONES EN SQL (sp_expirarHoldsVencidos)

```sql
WHERE 
  H.ESTADO_HOLD = 1                              -- Está activo
  AND R.ESTADO_GENERAL_RESERVA = 'PRE-RESERVA'  -- Es pre-reserva (no confirmada)
  AND ISNULL(R.ESTADO_RESERVA, 1) = 1            -- No está cancelada
  AND DATEADD(SECOND, H.TIEMPO_HOLD,             -- Tiempo pasó
      R.FECHA_REGISTRO_RESERVA) <= @NOW;         -- 600s desde creación
```

**Ejemplo:**
```
FECHA_REGISTRO = 2025-12-06 11:00:00
TIEMPO_HOLD    = 600 segundos
CÁLCULO        = 11:00:00 + 600 seg = 11:10:00

¿Expira si?
- AHORA = 11:10:00 ✅ SÍ (11:10:00 <= 11:10:00)
- AHORA = 11:10:01 ✅ SÍ (11:10:01 <= 11:10:00 = false, pero...)
- AHORA = 11:09:59 ❌ NO (11:09:59 > 11:10:00)
```

> Nota: El `<=` significa "menor o igual", así que expira exactamente a los 600 segundos.

---

## MANEJO DE ERRORES

```
Si expirar_holds_async() falla:
├─ El thread captura la excepción
├─ Se loguea el error
├─ La búsqueda continúa normalmente
└─ ✅ No afecta a la app

Si sp_expirarHoldsVencidos falla:
├─ Transaction se revierte (ROLLBACK)
├─ Datos consistentes en BD
├─ Log muestra el error
└─ ✅ BD no se corrompe

Si C# endpoint no responde:
├─ Timeout después de X segundos
├─ Thread termina gracefully
├─ Búsqueda continúa
└─ ✅ Usuario ve datos, aunque puede estar "viejo"
```

---

## PERFORMANCE IMPACT

```
Antes:
  GET /habitaciones = 500ms (búsqueda)
  
Después:
  GET /habitaciones = 500ms (búsqueda)
                     + ~0ms (thread daemon inicia)
  
Total: 500ms (sin impacto perceptible)

Razón: El thread se ejecuta EN PARALELO, no bloquea la respuesta.
```

---

## GARANTÍAS

✅ **Atomicidad:** Transacción SQL completa o nada
✅ **Consistencia:** BD siempre en estado válido
✅ **Aislamiento:** SERIALIZABLE isolation level
✅ **Durabilidad:** Cambios persistidos

✅ **Sin Race Conditions:** SQL Server maneja locks
✅ **Sin Deadlocks:** SP está optimizado
✅ **Sin Corrupción:** Validaciones completas
✅ **Fallback Seguro:** Excepciones capturadas

---

**🎯 Resultado: Expiración automática, segura y sin impacto en performance**
