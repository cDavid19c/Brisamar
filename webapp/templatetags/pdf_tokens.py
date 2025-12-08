from django import template
import hashlib

register = template.Library()

@register.filter
def pdf_secure_token(factura_id):
    """
    Genera un token único para cada factura.
    Este token se usa en la URL del PDF para que no sea manipulable.
    """
    # Clave secreta (la misma siempre)
    secret = "pdf_secure_key_2025"
    
    # Generar hash único: hash(factura_id + secret)
    data = f"{factura_id}_{secret}".encode()
    token = hashlib.sha256(data).hexdigest()[:16]
    
    return token
