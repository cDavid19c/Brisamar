import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class UsuarioExternoSoap:
    """
    Cliente SOAP para crear usuarios externos.
    Equivalente al servicio CrearUsuarioExternoWS.asmx
    """

    def __init__(self):
        self.wsdl = "http://soapbrisamar.runasp.net/CrearUsuarioExternoWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    def _normalize(self, d):
        """Normaliza la respuesta SOAP"""
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idUsuario": d.get("IdUsuario"),
            "bookingUserId": d.get("BookingUserId"),
            "nombre": d.get("Nombre"),
            "apellido": d.get("Apellido"),
            "correo": d.get("Correo"),
            "fechaCreacion": fmt(d.get("FechaCreacion")),
            "mensaje": d.get("Mensaje"),
            "estado": d.get("Estado")
        }

    def crear_usuario_externo(
        self,
        booking_user_id,
        nombre,
        apellido,
        correo
    ):
        """
        Crea un nuevo usuario externo en el sistema.
        
        Parámetros:
            booking_user_id (str): ID de usuario externo (obligatorio)
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            correo (str): Correo electrónico del usuario
            
        Retorna:
            Diccionario con los datos del usuario creado
        """
        
        if not booking_user_id:
            raise ValueError("booking_user_id es obligatorio.")
        if not nombre:
            raise ValueError("nombre es obligatorio.")
        if not apellido:
            raise ValueError("apellido es obligatorio.")
        if not correo:
            raise ValueError("correo es obligatorio.")

        try:
            # Preparar DTO para SOAP
            dto = {
                "BookingUserId": str(booking_user_id),
                "Nombre": nombre,
                "Apellido": apellido,
                "Correo": correo
            }

            # Llamada SOAP
            r = self.client.service.CrearUsuarioExterno(dto)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al crear usuario externo: {e}")
