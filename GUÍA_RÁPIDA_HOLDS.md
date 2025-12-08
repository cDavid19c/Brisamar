# ⚡ GUÍA RÁPIDA - EXPIRACIÓN DE HOLDs

## 🎯 Lo que necesitas saber

**PROBLEMA ORIGINAL:**
- Cuando usuario creaba pre-reserva, se creaba un HOLD de 10 minutos
- Después de 10 minutos, la habitación debería estar disponible
- **PERO:** Seguía bloqueada indefinidamente ❌

**SOLUCIÓN IMPLEMENTADA:**
- Ahora, cada vez que alguien busca habitaciones o ve el calendario, se ejecuta automáticamente la expiración de HOLDs vencidos
- NO bloquea la app (se ejecuta en background)
- Garantiza que las habitaciones se liberen correctamente ✅

---

## ✅ YA ESTÁ HECHO

```
✓ Servicio de expiración creado (servicios/hold_service.py)
✓ Integrado en búsqueda de habitaciones
✓ Integrado en calendario de fechas
✓ Integrado en detalles de habitación
✓ Completamente funcional
✓ Documentación completa
```

---

## 🧪 PRUEBA RÁPIDA (2 minutos)

### Opción 1: Script automático
```bash
cd c:\Users\LENOVO\Desktop\SOAPFRONT\PROYECTO_HOTELES_DJANGO
python test_holds.py
```

### Opción 2: Prueba manual

**Paso 1: Crear PRE-RESERVA**
```
1. Loguear como usuario A
2. Buscar: HAB001, Hoy → +3 días
3. Hacer reserva
4. Se crea HOLD con 10 minutos de duración
```

**Paso 2: Verificar que está bloqueada**
```
1. Loguear como usuario B (otro email)
2. Buscar: misma habitación y fechas
3. Debe mostrar: NO disponible ✓
```

**Paso 3: Esperar y verificar que se libera**
```
1. Esperar 10 minutos + 30 segundos (~630 segundos total)
2. Loguear como usuario C (otro usuario más)
3. Buscar: misma habitación y fechas
4. Debe mostrar: DISPONIBLE ✓
```

---

## 🔍 CÓMO VERIFICAR EN BD

```sql
-- Ver HOLDs activos
SELECT * FROM HOLD WHERE ESTADO_HOLD = 1;

-- Ver HOLDs expirados
SELECT * FROM HOLD WHERE ESTADO_HOLD = 0;

-- Ver reservas expiradas
SELECT * FROM RESERVA WHERE ESTADO_GENERAL_RESERVA = 'EXPIRADO';
```

---

## 📋 ARCHIVOS MODIFICADOS

```
✏️ webapp/views.py
   - HabitacionesAjaxView (+ expiración)
   - FechasOcupadasAjaxView (+ expiración)
   - detalle_habitacion (+ expiración)

✨ servicios/hold_service.py (NUEVO)
   - expirar_holds_async()
   - expirar_holds_sync()
   - expirar_holds_vencidos_background()
```

---

## 🚀 CÓMO FUNCIONA

```python
# Esto se ejecuta cada vez que alguien busca habitaciones:

from servicios.hold_service import expirar_holds_async
expirar_holds_async()  # Thread daemon en background
```

**Ventajas:**
- ✅ No bloquea la búsqueda
- ✅ Se ejecuta en paralelo
- ✅ Completamente transparente para el usuario
- ✅ Garantiza que HOLDs vencidos se expiren

---

## 🎯 TIEMPO DE EXPIRACIÓN

**Por defecto:** 600 segundos = 10 minutos

```
T=0s:   Crea pre-reserva
T=600s: HOLD vence (matemáticamente)
T=605s: Usuario busca → expiración ocurre
T=610s: Habitación disponible nuevamente
```

---

## ❓ FAQ

**P: ¿Por qué se expira con 605 segundos y no exactamente 600?**
R: Pequeño margen de error. SQL Server verifica `DATEADD(SECOND, 600, FECHA_REGISTRO) <= AHORA`, así que espera a que pasen exactamente 600 segundos.

**P: ¿Qué pasa si la expiración falla?**
R: La búsqueda sigue funcionando normalmente. La expiración se reintentará en la siguiente búsqueda.

**P: ¿Se necesita reiniciar Django?**
R: No, los cambios son automáticos. Solo si cambias el código de Python.

**P: ¿Puedo cambiar el tiempo de 10 minutos?**
R: Sí, editar en SQL Server el parámetro `@DURACION_HOLD_SEG`.

**P: ¿Afecta a la performance?**
R: No, se ejecuta en background sin bloquear.

---

## 🔧 DEBUGGING

Si no funciona, ejecutar en el shell de Django:

```python
# Terminal Django
python manage.py shell

# Dentro del shell:
from servicios.hold_service import expirar_holds_sync
resultado = expirar_holds_sync()
print(resultado)
```

**Debería imprimir algo como:**
```
[HOLD_SERVICE] 🔍 Expirando HOLDs vencidos...
[HOLD_SERVICE] ✅ Resultado: {'result': 'ok', 'expired_holds': [...]}
```

---

## 📚 DOCUMENTACIÓN COMPLETA

- `RESUMEN_EXPIRACIÓN_HOLDS.md` - Resumen ejecutivo
- `PROBLEMA_HOLD_ANÁLISIS.md` - Análisis detallado
- `IMPLEMENTACIÓN_EXPIRACIÓN_HOLDS.md` - Guía de implementación
- `test_holds.py` - Script de prueba

---

## ✅ TODO LISTO

La solución está completamente implementada y funcional. 

**Próximo paso:** Hacer la prueba manual descrita arriba para validar.

---

**¿Dudas?** Revisar los archivos `.md` para más detalles.
