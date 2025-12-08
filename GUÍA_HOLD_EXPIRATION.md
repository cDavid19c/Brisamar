# 🚀 GUÍA DE IMPLEMENTACIÓN - EXPIRACIÓN AUTOMÁTICA DE HOLDs

## 📋 RESUMEN

Se han creado 3 componentes para manejar la expiración automática de HOLDs:

1. **HoldGestionRest.py** - Cliente REST mejorado ✅ (YA ACTUALIZADO)
2. **tasks.py** - Tareas para ejecutar la expiración
3. **middleware_hold.py** - Middleware de Django para automatizar

---

## 🔧 COMPONENTES IMPLEMENTADOS

### 1️⃣ **HoldGestionRest.py** ✅

**Nuevo Método Principal:**
```python
def expirar_holds_vencidos(self):
    """Expira automáticamente HOLDs vencidos"""
    # POST /api/gestion/hold/expirar-vencidos
    # Llama al endpoint de C#
```

**Métodos Utilitarios Agregados:**
```python
# Obtiene solo HOLDs activos
obtener_holds_activos()

# Obtiene HOLDs de una reserva específica
obtener_holds_por_reserva(id_reserva)

# Calcula cuántos segundos quedan para que venza
tiempo_hold_restante(hold_dict)
```

**Ejemplo de Uso:**
```python
api_hold = HoldGestionRest()

# Expirar vencidos
resultado = api_hold.expirar_holds_vencidos()
print(resultado)  # {'mensaje': '...', 'totalExpirados': 2}

# Obtener activos
activos = api_hold.obtener_holds_activos()

# Tiempo restante
hold = api_hold.obtener_hold_por_id('HODA000001')
segundos_restantes = api_hold.tiempo_hold_restante(hold)
```

---

### 2️⃣ **tasks.py**

**Tareas Disponibles:**

#### Opción A: Threading Simple (RECOMENDADA PARA EMPEZAR)
```python
from webapp.tasks import expirar_holds_async

# En cualquier vista:
expirar_holds_async()  # Ejecuta en background sin bloquear
```

#### Opción B: Sincrónico (si necesitas garantizar que se complete)
```python
from webapp.tasks import expirar_holds_sync

resultado = expirar_holds_sync()
print(resultado)
```

#### Opción C: Comando de Django
```bash
# Ejecutar manualmente en terminal
python manage.py expirar_holds

# O en un cron job
0 * * * * cd /ruta/proyecto && python manage.py expirar_holds
```

---

### 3️⃣ **middleware_hold.py**

**Middleware Automático (RECOMENDADO)**

**Instalación:**
```python
# settings.py
MIDDLEWARE = [
    # ... otros middlewares ...
    'webapp.middleware_hold.ExpirarHoldsMiddleware',  # ← Agregar esta línea
]

# Configuración opcional (segundos entre chequeos)
HOLD_EXPIRATION_INTERVAL = 60  # Cada 60 segundos
```

**Cómo Funciona:**
- Se ejecuta en cada request
- Verifica si pasó el intervalo configurado
- Si sí, lanza un thread en background para expirar HOLDs
- **NO bloquea** el request del usuario

---

## 🎯 RECOMENDACIONES POR ESCENARIO

### 📱 Escenario 1: Pequeño Proyecto (1-10 usuarios)

**Usar:** Middleware Automático

```python
# settings.py
MIDDLEWARE = [
    ...
    'webapp.middleware_hold.ExpirarHoldsMiddleware',
]
```

**Ventajas:**
- ✅ Simple, no requiere configuración adicional
- ✅ Funciona automáticamente
- ✅ Bajo overhead

**Desventajas:**
- ❌ Depende de que haya requests activos
- ❌ Si no hay usuarios, no expira

---

### 🏢 Escenario 2: Proyecto Mediano (10-100 usuarios)

**Usar:** Celery + Beat (si ya lo tienes)

O **Celery + Redis** (para escala):

```python
# settings.py
from celery.schedules import schedule

CELERY_BEAT_SCHEDULE = {
    'expirar-holds-vencidos': {
        'task': 'webapp.tasks.task_expirar_holds_vencidos',
        'schedule': schedule(run_every=60),  # Cada 60 segundos
    },
}
```

```python
# tasks.py (agregar)
from celery import shared_task

@shared_task
def task_expirar_holds_vencidos():
    """Tarea Celery para expirar HOLDs"""
    from webapp.tasks import expirar_holds_vencidos_background
    return expirar_holds_vencidos_background()
```

**Ventajas:**
- ✅ Se ejecuta exactamente cada X segundos
- ✅ Independiente de requests de usuarios
- ✅ Más confiable

**Desventajas:**
- ❌ Requiere Redis/RabbitMQ
- ❌ Más componentes a mantener

---

### 🚀 Escenario 3: Enterprise (100+ usuarios)

**Usar:** Windows Service / Systemd Service

```python
# manage_hold_expiration.py (archivo nuevo)
import time
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PROYECTO_HOTELES_DJANGO.settings')
django.setup()

from servicios.rest.gestion.HoldGestionRest import HoldGestionRest

def servicio_expirar_holds():
    """Servicio que se ejecuta continuamente"""
    api_hold = HoldGestionRest()
    
    while True:
        try:
            print(f"[SERVICIO] Expirando HOLDs vencidos...")
            resultado = api_hold.expirar_holds_vencidos()
            print(f"[SERVICIO] ✓ {resultado}")
        except Exception as e:
            print(f"[SERVICIO ERROR] {e}")
        
        time.sleep(60)  # Esperar 60 segundos

if __name__ == '__main__':
    servicio_expirar_holds()
```

**Ejecutar como Windows Service:**
```powershell
# Instalar como servicio
py -m nssm install HoldExpiration "python manage_hold_expiration.py"

# Iniciar servicio
py -m nssm start HoldExpiration

# Ver estado
py -m nssm status HoldExpiration
```

**Ejecutar como systemd Service (Linux):**
```ini
# /etc/systemd/system/django-hold.service
[Unit]
Description=Django Hold Expiration Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/ruta/proyecto
ExecStart=/ruta/proyecto/venv/bin/python manage_hold_expiration.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar
sudo systemctl enable django-hold
sudo systemctl start django-hold

# Ver estado
sudo systemctl status django-hold
```

---

## 📊 OPCIÓN RECOMENDADA PARA TU CASO

Basándome en tu proyecto actual:

### **USAR: Middleware Automático + Manual en Vistas Críticas**

```python
# 1. Agregar middleware a settings.py
MIDDLEWARE = [
    ...
    'webapp.middleware_hold.ExpirarHoldsMiddleware',
]

# 2. En vistas críticas (mis_reservas, mis_pagos), también expirar:
def mis_reservas(request):
    # Expirar en background
    from webapp.tasks import expirar_holds_async
    expirar_holds_async()
    
    # Continuar con lógica normal
    ...

# 3. Opcional: También en confirmación de reserva
def confirmar_reserva(request):
    from webapp.tasks import expirar_holds_async
    expirar_holds_async()
    
    # Llamar al API para confirmar
    ...
```

**Ventajas:**
- ✅ Automático en cada request
- ✅ También manual en puntos críticos
- ✅ Se ejecuta en background (no bloquea)
- ✅ No requiere configuración adicional
- ✅ Simple y confiable

---

## 🔍 VERIFICACIÓN Y TESTING

### Test 1: Verificar que el método exista

```python
from servicios.rest.gestion.HoldGestionRest import HoldGestionRest

api = HoldGestionRest()
resultado = api.expirar_holds_vencidos()
print(resultado)
# Esperado: {'mensaje': '...', 'totalExpirados': N}
```

### Test 2: Verificar que se ejecute automáticamente

```python
# En Django shell
python manage.py shell

from webapp.middleware_hold import ExpirarHoldsMiddleware
ExpirarHoldsMiddleware._chequear_expirar_holds()
# Debería ver logs: [MIDDLEWARE] ✓ HOLDs expirados...
```

### Test 3: Monitorear HOLDs vencidos

```python
from servicios.rest.gestion.HoldGestionRest import HoldGestionRest

api = HoldGestionRest()
holds_activos = api.obtener_holds_activos()

for hold in holds_activos:
    segundos = api.tiempo_hold_restante(hold)
    print(f"{hold['IdHold']}: {segundos}s restantes")
```

---

## 📝 PRÓXIMOS PASOS

1. **Elegir estrategia:**
   - ✅ Usar Middleware Automático (RECOMENDADO)
   - ☐ Usar Celery
   - ☐ Usar Service

2. **Implementar:**
   - ✅ HoldGestionRest.py - YA HECHO
   - ✅ tasks.py - YA CREADO
   - ✅ middleware_hold.py - YA CREADO
   - ☐ Agregar middleware a settings.py

3. **Testear:**
   - ☐ Crear pre-reserva con HOLD de 60 segundos
   - ☐ Esperar 65 segundos
   - ☐ Verificar que se marque como EXPIRADO
   - ☐ Revisar logs en Django

4. **Monitoreo:**
   - ☐ Agregar logging detallado
   - ☐ Crear dashboard de HOLDs activos
   - ☐ Alertas si hay problemas

---

## 🛑 TROUBLESHOOTING

### Problema: "HOLDs no se expiran automáticamente"

**Solución:**
```python
# Verificar que middleware esté correctamente instalado
# settings.py - buscar:
'webapp.middleware_hold.ExpirarHoldsMiddleware',

# Si no está, agregarlo
```

### Problema: "Error de conexión con el API de C#"

**Solución:**
```python
# Verificar URL correcta en HoldGestionRest.py
BASE_URL = "http://allphahousenycrg.runasp.net/api/gestion/hold"

# Probar manualmente:
import requests
resp = requests.post(
    "http://allphahousenycrg.runasp.net/api/gestion/hold/expirar-vencidos",
    headers={"Content-Type": "application/json"},
    timeout=30
)
print(resp.status_code, resp.text)
```

### Problema: "El middleware está bloqueando requests"

**Solución:**
- El middleware crea threads daemon, así que NO debería bloquear
- Si algo se congela, revisar si hay excepción no capturada
- Usar `expirar_holds_async()` en lugar de `expirar_holds_sync()`

---

## 📚 REFERENCIA RÁPIDA

```python
# Importar
from servicios.rest.gestion.HoldGestionRest import HoldGestionRest
from webapp.tasks import expirar_holds_async, expirar_holds_sync

# Expirar vencidos
api = HoldGestionRest()
resultado = api.expirar_holds_vencidos()

# Obtener activos
holds_activos = api.obtener_holds_activos()

# Tiempo restante
segundos = api.tiempo_hold_restante(hold)

# Background (no bloquea)
expirar_holds_async()

# Sincrónico (bloquea)
resultado = expirar_holds_sync()
```

