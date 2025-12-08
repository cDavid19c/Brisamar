# 📋 ANÁLISIS DE LA LÓGICA DE HOLD - SISTEMA DE EXPIRACIÓN

## 🎯 OBJETIVO
Automatizar la expiración de HOLDs (reservas temporales) cuando el usuario no confirma la reserva en el tiempo asignado.

---

## 📊 ARQUITECTURA ACTUAL

### 1️⃣ **BASE DE DATOS - SP: sp_expirarHoldsVencidos**

```sql
-- ENTRADA: Ninguna (se ejecuta automáticamente)
-- SALIDA: Actualiza tablas HOLD y RESERVA

LÓGICA:
1. Obtener HOLD AHORA = GETDATE()
2. BUSCAR todos los HOLD/RESERVA donde:
   ├─ HOLD.ESTADO_HOLD = 1 (activo)
   ├─ RESERVA.ESTADO_GENERAL_RESERVA = 'PRE-RESERVA'
   ├─ RESERVA.ESTADO_RESERVA = 1 (válido)
   └─ FECHA_REGISTRO_RESERVA + TIEMPO_HOLD(segundos) <= AHORA
      
3. PARA CADA HOLD VENCIDO:
   ├─ HOLD.ESTADO_HOLD = 0 (marcar como inactivo)
   └─ RESERVA.ESTADO_GENERAL_RESERVA = 'EXPIRADO' (marcar como expirada)
```

### 2️⃣ **BACKEND C# - CAPA DE DATOS (GD)**

```csharp
public void ExpirarHoldsVencidos()
{
    using (var cn = new SqlConnection(CadenaConexion))
    using (var cmd = new SqlCommand("dbo.sp_expirarHoldsVencidos", cn))
    {
        cmd.CommandType = CommandType.StoredProcedure;
        cn.Open();
        cmd.ExecuteNonQuery();  // ← Ejecuta el SP sin retornar datos
    }
}

// ✅ Simple y directo: solo llama al SP
// ✅ Sin parámetros de entrada/salida
// ✅ Sin validaciones (el SP las hace)
```

### 3️⃣ **BACKEND C# - CAPA DE LÓGICA (LN)**

```csharp
public void ExpirarHoldsVencidos()
{
    _gd.ExpirarHoldsVencidos();  // ← Delega al GD
}

// ✅ Patrón de tres capas respetado
// ✅ LN solo orquesta, GD ejecuta
```

### 4️⃣ **BACKEND C# - CONTROLADOR (REST)**

```csharp
[HttpPost]
[Route("expirar-vencidos")]
public IHttpActionResult ExpirarHoldsVencidos()
{
    _ln.ExpirarHoldsVencidos();
    return Ok(new { mensaje = "Holds vencidos expirados correctamente." });
}

// ✅ Endpoint: POST /api/v1/hoteles/holds/expirar-vencidos
// ✅ No requiere parámetros
// ✅ Retorna mensaje de éxito
// ❌ No retorna datos de qué HOLDs se expiraron
```

---

## 🔄 FLUJO COMPLETO

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE EXPIRACIÓN DE HOLD                   │
└─────────────────────────────────────────────────────────────────┘

ESCENARIO:
- Usuario crea pre-reserva: HOLD se crea con TIEMPO_HOLD = 180 seg (3 min)
- Usuario NO confirma en 3 minutos
- Sistema detecta y expira automáticamente

LÍNEA DE TIEMPO:
```

**T = 0 seg (Creación de pre-reserva)**
```
HOLD creado:
├─ ID_HOLD = HODA000001
├─ ESTADO_HOLD = 1 (activo)
├─ TIEMPO_HOLD = 180 (segundos)
└─ FECHA_INICIO_HOLD = 2025-12-06 11:00:00

RESERVA creada:
├─ ID_RESERVA = 100
├─ ESTADO_GENERAL_RESERVA = 'PRE-RESERVA'
├─ ESTADO_RESERVA = 1 (válida)
└─ FECHA_REGISTRO_RESERVA = 2025-12-06 11:00:00
```

**T = 180 seg + 1 seg (3 minutos y 1 segundo después)**
```
Se ejecuta sp_expirarHoldsVencidos()

CÁLCULO:
DATEADD(SECOND, 180, 2025-12-06 11:00:00) = 2025-12-06 11:03:00
GETDATE() = 2025-12-06 11:03:01

¿11:03:00 <= 11:03:01? ✅ SÍ → EXPIRAR

HOLD actualizado:
├─ ESTADO_HOLD = 0 (inactivo)
└─ FECHA_FINAL_HOLD = (se actualiza en confirmación)

RESERVA actualizada:
├─ ESTADO_GENERAL_RESERVA = 'EXPIRADO'
├─ ESTADO_RESERVA = 0 (inválida)
└─ FECHA_MODIFICACION_RESERVA = 2025-12-06 11:03:01
```

---

## 🔌 INTEGRACIÓN CON DJANGO

### Opción 1: Sincrónica (Bloqueante)
```python
# views.py
def alguna_vista(request):
    # Antes de cualquier operación crítica
    api_hold = HoldGestionRest()
    api_hold.expirar_holds_vencidos()  # Llama al endpoint de C#
    
    # Luego continúa con la lógica normal
    reservas = api_reserva.obtener_reservas()
    # ...
```

**Ventajas:**
- ✅ Simples de implementar
- ✅ Garantiza datos actualizados

**Desventajas:**
- ❌ Agrega latencia a cada request
- ❌ Si C# es lento, Django se congela

### Opción 2: Asincrónica (No bloqueante) - **RECOMENDADA**
```python
# Celery task
@shared_task
def expirar_holds_vencidos():
    """Ejecutar cada X segundos automáticamente"""
    api_hold = HoldGestionRest()
    api_hold.expirar_holds_vencidos()
    return {"status": "completado"}

# En settings.py
CELERY_BEAT_SCHEDULE = {
    'expirar-holds-vencidos': {
        'task': 'webapp.tasks.expirar_holds_vencidos',
        'schedule': timedelta(seconds=60),  # Cada 60 segundos
    },
}
```

**Ventajas:**
- ✅ No bloquea las vistas
- ✅ Se ejecuta automáticamente
- ✅ Más escalable

**Desventajas:**
- ❌ Requiere configurar Celery + Redis/RabbitMQ
- ❌ Más complejo de testear

### Opción 3: Híbrida (RECOMENDADA PARA TU CASO)
```python
# views.py - En vistas críticas
def mis_reservas(request):
    # Expirar holds de forma asincrónica, sin bloquear
    from threading import Thread
    
    def expirar_en_background():
        try:
            api_hold = HoldGestionRest()
            api_hold.expirar_holds_vencidos()
        except Exception as e:
            print(f"[WARN] Error al expirar holds: {e}")
    
    # Ejecutar en background sin esperar
    thread = Thread(target=expirar_en_background, daemon=True)
    thread.start()
    
    # Continuar con la lógica sin esperar
    reservas = api_reserva.obtener_reservas()
    return render(request, 'pagos.html', {'reservas': reservas})
```

---

## 🛠️ MEJORAS SUGERIDAS

### 1. Retornar datos de qué se expiró

**ACTUAL (C#):**
```csharp
return Ok(new { mensaje = "Holds vencidos expirados correctamente." });
```

**MEJORADO (C#):**
```csharp
// Modificar SP para retornar datos
-- En el SP, agregar al final:
SELECT COUNT(*) as TotalExpirados FROM @HExp;

// En el GD, retornar el valor
public int ExpirarHoldsVencidos()
{
    using (var cn = new SqlConnection(CadenaConexion))
    using (var cmd = new SqlCommand("dbo.sp_expirarHoldsVencidos", cn))
    {
        cmd.CommandType = CommandType.StoredProcedure;
        cn.Open();
        return (int)cmd.ExecuteScalar();  // ← Retorna count
    }
}

// En el LN
public int ExpirarHoldsVencidos()
{
    return _gd.ExpirarHoldsVencidos();
}

// En el Controlador
[HttpPost]
[Route("expirar-vencidos")]
public IHttpActionResult ExpirarHoldsVencidos()
{
    int totalExpirados = _ln.ExpirarHoldsVencidos();
    return Ok(new { 
        mensaje = "Holds vencidos expirados correctamente.",
        totalExpirados = totalExpirados
    });
}
```

### 2. Agregar endpoint para ver HOLDs vencidos

```csharp
[HttpGet]
[Route("vencidos")]
public IHttpActionResult ObtenerHoldsVencidos()
{
    var holds = _ln.ObtenerHoldsVencidos();
    return Ok(holds);
}
```

### 3. Logging mejorado en C#

```csharp
public void ExpirarHoldsVencidos()
{
    _logger.Info("[HOLD] Iniciando expiración de holds vencidos...");
    
    try
    {
        int totalExpirados = _gd.ExpirarHoldsVencidos();
        _logger.Info($"[HOLD] {totalExpirados} holds expirados correctamente");
    }
    catch (Exception ex)
    {
        _logger.Error($"[ERROR HOLD] Error al expirar holds: {ex.Message}");
        throw;
    }
}
```

---

## 📌 PUNTOS CLAVE

| Aspecto | Descripción |
|--------|------------|
| **Activador** | Puede ser manual (POST) o automático (Celery/Timer) |
| **Condición de expiración** | FECHA_REGISTRO + TIEMPO_HOLD <= AHORA |
| **Estados antes** | HOLD.ESTADO_HOLD=1, RESERVA=PRE-RESERVA |
| **Estados después** | HOLD.ESTADO_HOLD=0, RESERVA=EXPIRADO |
| **Datos en BD** | Los datos quedan intactos, solo se marcan como expirados |
| **Recuperación** | Una vez expirado, el usuario NO puede confirmar (el SP lo valida) |

---

## ⚠️ CASOS ESPECIALES A CONSIDERAR

### ¿Qué pasa si el usuario intenta confirmar DESPUÉS de expirar?

En el SP `sp_reservarHabitacionUsuarioInterno` (línea 114-127), ya hay validación:
```sql
IF @ESTADO_GENERAL_RESERVA <> 'PRE-RESERVA' OR @ESTADO_RESERVA = 0
BEGIN
    RAISERROR('La pre-reserva ya no está vigente (cancelada, confirmada o expirada).',16,1);
    ROLLBACK TRANSACTION;
    RETURN;
END;
```

✅ **Está correctamente validado**

### ¿Qué pasa con los HOLDs que ya vencieron hace días?

El SP verifica `DATEADD(SECOND, TIEMPO_HOLD, ...) <= @NOW`, así que:
- Si un HOLD fue creado hace 10 minutos con TIEMPO_HOLD=180 seg (3 min)
- Y ahora es 1 hora después
- El SP lo detectará y expirará igualmente ✅

### ¿El usuario puede ver sus HOLDs expirados?

Sí, porque en `MisReservasView` (views.py), se cargan todas las reservas con:
```python
if estado_reserva.strip().upper() == "CANCELADA":
    continue

# No filtra EXPIRADO, así que aparecen en la lista ✅
```

---

## 🎓 RESUMEN ARQUITECTÓNICO

```
┌─────────────────────────────────────────────────────┐
│           FLUJO DE EXPIRACIÓN DE HOLDS               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Usuario NO confirma en TIEMPO_HOLD segundos     │
│     ↓                                                │
│  2. Se ejecuta: POST /expirar-vencidos              │
│     ↓                                                │
│  3. C# Controlador → LN → GD → SP                  │
│     ↓                                                │
│  4. SP busca: DATEADD(SECOND, TIEMPO_HOLD, ...)    │
│              <= GETDATE()                           │
│     ↓                                                │
│  5. Marca: HOLD.ESTADO = 0                         │
│           RESERVA.ESTADO = EXPIRADO                │
│     ↓                                                │
│  6. BD Updated ✅                                    │
│     ↓                                                │
│  7. Usuario ve "EXPIRADO" en su lista de reservas   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 PRÓXIMAS ACCIONES SUGERIDAS

1. ✅ Crear cliente REST en Django para llamar el endpoint
2. ✅ Implementar expiración automática (Celery o Thread)
3. ✅ Agregar logging mejorado
4. ✅ Crear endpoint GET para monitorear HOLDs vencidos
5. ✅ Testear comportamiento con HOLDs reales

