import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class PreReservaSoap:
    """
    Cliente SOAP para crear una pre-reserva (hold).
    Equivalente al servicio CrearPreReservaWS.asmx
    """

    def __init__(self):
        self.wsdl = "http://soapbrisamar.runasp.net/CrearPreReservaWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    def _normalize(self, d):
        """Normaliza un objeto de respuesta SOAP"""
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idHold": d.get("IdHold"),
            "idHabitacion": d.get("IdHabitacion"),
            "idUsuario": d.get("IdUsuario"),
            "fechaInicio": fmt(d.get("FechaInicio")),
            "fechaFin": fmt(d.get("FechaFin")),
            "numeroHuespedes": d.get("NumeroHuespedes"),
            "precioCalculado": d.get("PrecioCalculado"),
            "fechaExpiracionHold": fmt(d.get("FechaExpiracionHold")),
            "estadoHold": d.get("EstadoHold"),
            "mensaje": d.get("Mensaje"),
            "nombre": d.get("Nombre"),
            "apellido": d.get("Apellido"),
            "correo": d.get("Correo"),
            "tipoDocumento": d.get("TipoDocumento"),
            "documento": d.get("Documento")
        }

    @staticmethod
    def _to_iso(dt):
        """Convierte string o datetime → ISO 8601"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        if isinstance(dt, str):
            return dt
        return None

    def crear_prereserva(
        self,
        id_habitacion,
        fecha_inicio,
        fecha_fin,
        numero_huespedes,
        nombre,
        apellido,
        correo,
        tipo_documento,
        documento,
        duracion_hold_seg=None,
        precio_actual=None
    ):
        """
        Crea una pre-reserva (hold) en el sistema.
        
        Parámetros:
            id_habitacion (str): ID de la habitación
            fecha_inicio (datetime/str): Fecha de inicio
            fecha_fin (datetime/str): Fecha de fin
            numero_huespedes (int): Número de huéspedes
            nombre (str): Nombre del huésped
            apellido (str): Apellido del huésped
            correo (str): Correo electrónico
            tipo_documento (str): Tipo de documento
            documento (str): Número de documento
            duracion_hold_seg (int, optional): Duración del hold en segundos
            precio_actual (float, optional): Precio actual de la habitación
            
        Retorna:
            Diccionario con los datos del hold creado
        """
        
        # Validaciones básicas
        if not id_habitacion:
            raise ValueError("Debe indicar idHabitacion.")
        if fecha_fin <= fecha_inicio:
            raise ValueError("fechaFin debe ser mayor a fechaInicio.")
        if numero_huespedes <= 0:
            raise ValueError("numeroHuespedes debe ser mayor que 0.")

        try:
            # Preparar DTO para SOAP
            dto = {
                "IdHabitacion": str(id_habitacion),
                "FechaInicio": self._to_iso(fecha_inicio),
                "FechaFin": self._to_iso(fecha_fin),
                "NumeroHuespedes": numero_huespedes,
                "Nombre": nombre,
                "Apellido": apellido,
                "Correo": correo,
                "TipoDocumento": tipo_documento,
                "Documento": documento,
                "DuracionHoldSeg": duracion_hold_seg,
                "PrecioActual": precio_actual
            }

            # Llamada SOAP
            r = self.client.service.CrearPreReserva(dto)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al crear pre-reserva: {e}")
