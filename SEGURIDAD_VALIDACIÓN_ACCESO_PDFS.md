# 🔒 SEGURIDAD CRÍTICA - VALIDACIÓN DE ACCESO A PDFs Y FACTURAS

## 🚨 VULNERABILIDAD IDENTIFICADA

**Problema:**
- Endpoints `/api/generar-factura/` y `/api/generar-pdf-reserva/` permitían acceso a facturas de OTROS usuarios
- Si se conocía el ID de una factura, cualquier usuario logueado podía:
  - Generar la factura de otro usuario
  - Descargar el PDF de otra persona
  - Acceder a datos confidenciales (email, documento, total pagado, etc.)

**Severidad:** 🔴 **CRÍTICA - Violación de privacidad**

---

## ✅ SOLUCIÓN IMPLEMENTADA

### 2 Validaciones de Seguridad Agregadas

#### 1️⃣ En `generar_factura()` (línea ~1575)
```python
# 🔑 VALIDACIÓN 1: Verificar autenticación
if not request.user.is_authenticated:
    return JsonResponse({"ok": False, "error": "Debes estar logueado"}, status=401)

# 🔑 VALIDACIÓN 2: Verificar propiedad de reserva
reserva_valida = None
for res in reservas_usuario:
    if res.get("IdReserva") == id_reserva_int:
        email_reserva = res.get("EmailUsuario") or res.get("EMAIL_USUARIO")
        email_usuario = request.user.email
        
        if email_usuario and email_reserva and email_usuario.lower() == email_reserva.lower():
            reserva_valida = res
            break

if not reserva_valida:
    # ❌ BLOQUEAR ACCESO
    return JsonResponse(
        {"ok": False, "error": "No tienes permiso para generar factura de esta reserva"}, 
        status=403
    )
```

#### 2️⃣ En `generar_pdf_reserva()` (línea ~1696)
```python
# 🔑 VALIDACIÓN 1: Verificar autenticación
if not request.user.is_authenticated:
    return JsonResponse({"ok": False, "error": "Debes estar logueado"}, status=401)

# 🔑 VALIDACIÓN 2: Verificar propiedad de factura
email_factura = factura.get("EmailUsuario") or factura.get("EmailUsuarioExterno")
email_usuario = request.user.email

if not email_usuario or not email_factura or email_usuario.lower() != email_factura.lower():
    # ❌ BLOQUEAR ACCESO
    return JsonResponse(
        {"ok": False, "error": "No tienes permiso para acceder a esta factura"},
        status=403
    )
```

---

## 🔄 FLUJO DE SEGURIDAD

### Antes (Vulnerable)
```
Usuario A:
  └─ POST /api/generar-factura/
     ├─ body: {"idReserva": 999}  (de otro usuario)
     └─ ✅ Acceso permitido ❌ PROBLEMA
     
Usuario B (hacker):
  └─ Accede a factura de Usuario A
     ├─ Obtiene email
     ├─ Obtiene total
     ├─ Descarga PDF
     └─ ❌ VIOLACIÓN DE PRIVACIDAD
```

### Después (Seguro)
```
Usuario A:
  └─ POST /api/generar-factura/
     ├─ body: {"idReserva": 999}  (intenta otro usuario)
     ├─ Validación 1: ¿Está logueado? ✅ Sí
     ├─ Validación 2: ¿La reserva es suya? ❌ No
     └─ Response: 403 Forbidden ✅
     
Usuario B (hacker):
  └─ Intenta acceder a factura de Usuario A
     ├─ La validación rechaza
     └─ ❌ ACCESO DENEGADO ✅
```

---

## 📊 VALIDACIONES IMPLEMENTADAS

| Punto | Antes | Después |
|-------|-------|---------|
| **Autenticación** | ❌ No verificada | ✅ Verificada |
| **Propiedad de Reserva** | ❌ No validada | ✅ Validada por email |
| **Propiedad de Factura** | ❌ No validada | ✅ Validada por email |
| **Logging de intentos** | ❌ No | ✅ [SECURITY] logs |
| **HTTP Status** | 200/400 | 401/403/400 |

---

## 🔐 MECANISMO DE VALIDACIÓN

### Comparación por Email
```python
# Se compara el email del usuario logueado con el email de la reserva/factura
if email_usuario.lower() == email_factura.lower():
    # ✅ Permitir acceso
else:
    # ❌ Rechazar (403 Forbidden)
```

**Por qué email:**
- Email es único por usuario
- Viene en el JWT/sesión de autenticación
- Es verificado en la BD

### Validación en Dos Niveles
```
1. ¿Está autenticado? (401 Unauthorized)
   ↓ Sí
2. ¿Es su recurso? (403 Forbidden)
   ↓ Sí
3. ✅ Permitir operación
```

---

## 📝 ARCHIVOS MODIFICADOS

**Archivo:** `webapp/views.py`

### Cambio 1: `generar_factura()` (línea ~1575)
- **Agregado:** Autenticación + Validación de propiedad
- **Líneas nuevas:** ~20 líneas
- **Efecto:** Bloquea acceso a facturas de otros usuarios

### Cambio 2: `generar_pdf_reserva()` (línea ~1696)
- **Agregado:** Autenticación + Validación de propiedad
- **Líneas nuevas:** ~15 líneas
- **Efecto:** Bloquea descarga de PDFs de otros usuarios

---

## 🧪 PRUEBA DE SEGURIDAD

### Caso 1: Usuario Logueado - Su Propia Factura
```
Usuario A (email: usuario_a@test.com)
POST /api/generar-factura/
{
    "idReserva": 100,  ← Reserva de usuario_a@test.com
    "nombre": "A",
    "apellido": "User",
    "correo": "usuario_a@test.com",
    "documento": "123456"
}

✅ Respuesta 200: Factura generada
```

### Caso 2: Usuario Intenta Acceder a Factura Ajena
```
Usuario B (email: usuario_b@test.com)
POST /api/generar-factura/
{
    "idReserva": 100,  ← Reserva de usuario_a@test.com
    "nombre": "B",
    "apellido": "User",
    "correo": "usuario_b@test.com",
    "documento": "654321"
}

❌ Respuesta 403: "No tienes permiso para generar factura de esta reserva"
```

### Caso 3: Usuario NO Logueado
```
POST /api/generar-factura/
(sin autenticación)

❌ Respuesta 401: "Debes estar logueado"
```

---

## 📊 LOGS DE SEGURIDAD

Cuando se detecta un intento de acceso no autorizado:

```
[SECURITY] ⚠️ Intento de acceso no autorizado a reserva 999
[SECURITY] Usuario: usuario_b@test.com
```

```
[SECURITY] ⚠️ Intento de acceso no autorizado a factura 999
[SECURITY] Usuario: usuario_b@test.com | Factura: usuario_a@test.com
```

Esto permite:
- ✅ Auditoría de intentos de hackeo
- ✅ Investigación de incidentes de seguridad
- ✅ Alertas automáticas si se detectan patrones

---

## 🛡️ PROTECCIONES ADICIONALES

### Nivel de Aplicación
- ✅ Validación de autenticación (JWT/Session)
- ✅ Validación de propiedad (email matching)
- ✅ Logging de intentos de acceso no autorizado

### Nivel de Transporte
- ✅ HTTPS (asumido en producción)
- ✅ CSRF protection (Django)
- ✅ CORS policy (si aplica)

### Nivel de BD
- ✅ Transacciones ACID
- ✅ Validación en SP (sp_emitirFacturaHotel_Interno)
- ✅ Integridad referencial

---

## ✅ CHECKLIST DE SEGURIDAD

- ✅ Autenticación verificada
- ✅ Propiedad validada
- ✅ HTTP status codes correctos
- ✅ Logging implementado
- ✅ Mensajes de error seguros (no revelan info)
- ✅ No hay inyección SQL (uso de ORM/API)
- ✅ No hay XSS (respuesta JSON)
- ✅ Backwards compatible (solo agrega validaciones)

---

## 🚀 IMPLEMENTACIÓN

**Estado:** ✅ COMPLETADO

**Cambios:**
- 2 funciones modificadas
- ~35 líneas de código agregadas
- Sin cambios en BD
- Sin cambios en C#
- Sin cambios en API

**Testing:**
```bash
# Crear 2 usuarios diferentes
# Usuario A: Crear pre-reserva y factura
# Usuario B: Intentar acceder a factura de A
#   → Debe obtener 403 Forbidden ✅
```

---

## 📞 IMPACTO EN USUARIO

**Para Usuario Legítimo:**
- ✅ Sin cambios (acceso funciona normal)
- ✅ Seguridad mejorada

**Para Hacker/Atacante:**
- ❌ Imposible acceder a datos de otros usuarios
- ❌ HTTP 403 si intenta
- ✅ Intento registrado en logs

---

**Status: 🟢 SEGURIDAD CRÍTICA IMPLEMENTADA**
