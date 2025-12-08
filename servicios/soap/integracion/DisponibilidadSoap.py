import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class DisponibilidadSoap:
    """
    Cliente SOAP para verificar disponibilidad de habitaciones.
    Equivalente al servicio ValidarDisponibilidadWS.asmx
    """

    def __init__(self):
        self.wsdl = "http://soapbrisamar.runasp.net/ValidarDisponibilidadWS.asmx?wsdl"

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
            "disponible": d.get("Disponible"),
            "idHabitacion": d.get("IdHabitacion"),
            "fechaInicio": fmt(d.get("FechaInicio")),
            "fechaFin": fmt(d.get("FechaFin")),
            "mensaje": d.get("Mensaje"),
            "precio": d.get("Precio"),
            "capacidadDisponible": d.get("CapacidadDisponible")
        }

    @staticmethod
    def _to_iso(dt):
        """Convierte string o datetime → ISO 8601"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        if isinstance(dt, str):
            return dt
        return None

    def validar_disponibilidad(self, id_habitacion, fecha_inicio, fecha_fin):
        """
        Valida si una habitación está disponible en el rango de fechas.
        
        Parámetros:
            id_habitacion (str/int): ID de la habitación
            fecha_inicio (datetime/str): Fecha de inicio
            fecha_fin (datetime/str): Fecha de fin
            
        Retorna:
            Diccionario con disponibilidad y detalles
        """
        
        # Validaciones previas
        if not id_habitacion:
            raise ValueError("El campo 'id_habitacion' es obligatorio.")
        
        if fecha_fin <= fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor que fecha_inicio.")

        try:
            # Preparar DTO para SOAP
            dto = {
                "IdHabitacion": str(id_habitacion),
                "FechaInicio": self._to_iso(fecha_inicio),
                "FechaFin": self._to_iso(fecha_fin)
            }

            # Llamada SOAP
            r = self.client.service.ValidarDisponibilidad(dto)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al validar disponibilidad: {e}")
