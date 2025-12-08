import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class ConfirmarReservaSoap:
    """
    Cliente SOAP para confirmar una reserva.
    Equivalente al servicio ReservarHabitacionWS.asmx
    """

    def __init__(self):
        self.wsdl = "http://allpahousenyc.runasp.net/ReservarHabitacionWS.asmx?wsdl"

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
            "idReserva": d.get("IdReserva"),
            "idHabitacion": d.get("IdHabitacion"),
            "idHold": d.get("IdHold"),
            "idUsuario": d.get("IdUsuario"),
            "fechaInicio": fmt(d.get("FechaInicio")),
            "fechaFin": fmt(d.get("FechaFin")),
            "numeroHuespedes": d.get("NumeroHuespedes"),
            "estadoReserva": d.get("EstadoReserva"),
            "costoTotal": d.get("CostoTotal"),
            "fechaReserva": fmt(d.get("FechaReserva")),
            "mensaje": d.get("Mensaje"),
            "nombre": d.get("Nombre"),
            "apellido": d.get("Apellido"),
            "correo": d.get("Correo"),
            "tipoDocumento": d.get("TipoDocumento")
        }

    @staticmethod
    def _to_iso(dt):
        """Convierte string o datetime → ISO 8601"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        if isinstance(dt, str):
            return dt
        return None

    def confirmar_reserva(
        self,
        id_habitacion,
        id_hold,
        nombre,
        apellido,
        correo,
        tipo_documento,
        fecha_inicio,
        fecha_fin,
        numero_huespedes
    ):
        """
        Confirma una reserva existente.
        
        Parámetros:
            id_habitacion (str): ID de la habitación
            id_hold (str): ID del hold
            nombre (str): Nombre del huésped
            apellido (str): Apellido del huésped
            correo (str): Correo electrónico
            tipo_documento (str): Tipo de documento
            fecha_inicio (datetime/str): Fecha de inicio
            fecha_fin (datetime/str): Fecha de fin
            numero_huespedes (int): Número de huéspedes
            
        Retorna:
            Diccionario con los datos de la reserva confirmada
        """
        
        # Validaciones previas
        if not id_habitacion:
            raise ValueError("El campo 'id_habitacion' es obligatorio.")
        if not id_hold:
            raise ValueError("El campo 'id_hold' es obligatorio.")
        if not nombre:
            raise ValueError("El campo 'nombre' es obligatorio.")
        if not apellido:
            raise ValueError("El campo 'apellido' es obligatorio.")
        if not correo:
            raise ValueError("El campo 'correo' es obligatorio.")
        if not tipo_documento:
            raise ValueError("El campo 'tipo_documento' es obligatorio.")
        if fecha_fin <= fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor que fecha_inicio.")
        if numero_huespedes <= 0:
            raise ValueError("numero_huespedes debe ser mayor que 0.")

        try:
            # Preparar DTO para SOAP
            dto = {
                "IdHabitacion": str(id_habitacion),
                "IdHold": str(id_hold),
                "Nombre": nombre,
                "Apellido": apellido,
                "Correo": correo,
                "TipoDocumento": tipo_documento,
                "FechaInicio": self._to_iso(fecha_inicio),
                "FechaFin": self._to_iso(fecha_fin),
                "NumeroHuespedes": numero_huespedes
            }

            # Llamada SOAP
            r = self.client.service.ReservarHabitacion(dto)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al confirmar reserva: {e}")
