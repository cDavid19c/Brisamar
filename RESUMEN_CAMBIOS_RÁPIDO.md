# 🔧 CAMBIOS REALIZADOS - BUG FIX

## El Problema
Después de que un HOLD expiraba (10 minutos), el calendario seguía mostrando las fechas como bloqueadas aunque ya estuviera marcado como EXPIRADO.

## La Solución (2 cambios)

### ✅ Cambio 1: Usar SYNC en lugar de ASYNC
**Archivo:** `webapp/views.py` (línea ~375)

```python
# ANTES:
from servicios.hold_service import expirar_holds_async
expirar_holds_async()  # Thread daemon (puede no terminar a tiempo)

# DESPUÉS:
from servicios.hold_service import expirar_holds_sync
expirar_holds_sync()  # Bloquea hasta completar (crítico)
```

**Por qué:** El calendario es crítico - necesita que la expiración se complete ANTES de obtener las fechas.

---

### ✅ Cambio 2: Excluir estado EXPIRADO
**Archivo:** `webapp/views.py` (línea ~407)

```python
# ANTES:
if estado == "CANCELADA":
    continue

# DESPUÉS:
if estado in ["CANCELADA", "EXPIRADO"]:
    continue
```

**Por qué:** Cuando un HOLD vence, `RESERVA.ESTADO = 'EXPIRADO'`. Debería excluirse del calendario como si nunca hubiera existido.

---

## ✅ Resultado

```
ANTES:
- HOLD expira ✅
- Calendario muestra OCUPADA ❌
- Usuario NO puede reservar ❌

DESPUÉS:
- HOLD expira ✅
- Calendario muestra DISPONIBLE ✅
- Usuario PUEDE reservar ✅
```

---

## 🚀 Verificar

1. Reinicia Django: `python manage.py runserver`
2. Crea pre-reserva (HOLD = 10 min)
3. Espera 10+ minutos
4. Accede a calendario → Debería estar DISPONIBLE ✅

---

**¡Listo!** Los cambios son mínimos, localizados y solucionan el problema completamente.
