import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class HabitacionesSoap:
    """
    Cliente SOAP para consultar habitaciones disponibles.
    Equivalente al servicio buscarHabitacionesWS.asmx
    """

    def __init__(self):
        self.wsdl = "http://soapbrisamar.runasp.net/buscarHabitacionesWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    def _normalize(self, d):
        """Normaliza un objeto de respuesta SOAP a diccionario Python"""
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        # El servicio SOAP retorna los campos en PascalCase
        return {
            "id": d.get("Id"),
            "idHabitacion": d.get("IdHabitacion"),
            "nombre": d.get("NombreHabitacion"),
            "nombreHabitacion": d.get("NombreHabitacion"),
            "tipo": d.get("TipoHabitacion"),
            "tipoHabitacion": d.get("TipoHabitacion"),
            "tipoNombre": d.get("TipoNombre"),
            "capacidad": d.get("Capacidad"),
            "precio": d.get("PrecioVigente") or d.get("PrecioActual") or d.get("PrecioNormal"),
            "precioVigente": d.get("PrecioVigente") or d.get("PrecioActual") or d.get("PrecioNormal"),
            "precioActual": d.get("PrecioActual") or d.get("PrecioVigente") or d.get("PrecioNormal"),
            "hotel": d.get("NombreHotel"),
            "nombreHotel": d.get("NombreHotel"),
            "ubicacion": d.get("NombreCiudad"),
            "nombreCiudad": d.get("NombreCiudad"),
            "nombrePais": d.get("NombrePais"),
            "imagen": d.get("Imagen"),
            "imagenes": d.get("Imagen"),
            "servicios": d.get("Servicios"),
            "descripcion": d.get("Descripcion"),
            "disponible": d.get("Disponible"),
            "fechaDesde": fmt(d.get("FechaDesde")),
            "fechaHasta": fmt(d.get("FechaHasta"))
        }

    @staticmethod
    def _to_iso(dt):
        """Convierte string o datetime → ISO 8601"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        if isinstance(dt, str):
            return dt
        return None

    def buscar_habitaciones(
        self,
        date_from=None,
        date_to=None,
        tipo_habitacion=None,
        capacidad=None,
        precio_min=None,
        precio_max=None
    ):
        """
        Busca habitaciones disponibles con filtros opcionales.
        
        Parámetros:
            date_from (datetime/str): Fecha de inicio de disponibilidad
            date_to (datetime/str): Fecha de fin de disponibilidad
            tipo_habitacion (str): Tipo de habitación
            capacidad (int): Capacidad mínima
            precio_min (float): Precio mínimo
            precio_max (float): Precio máximo
            
        Retorna:
            Lista de habitaciones disponibles
        """
        try:
            # Preparar parámetros (todos opcionales) - usar snake_case según firma SOAP
            params = {
                "date_from": self._to_iso(date_from) if date_from else None,
                "date_to": self._to_iso(date_to) if date_to else None,
                "tipo_habitacion": tipo_habitacion,
                "capacidad": capacidad,
                "precio_min": precio_min,
                "precio_max": precio_max
            }

            # Llamada SOAP
            r = self.client.service.buscarHabitaciones(**params)
            r = serialize_object(r)

            # Normalizar lista de resultados
            if isinstance(r, list):
                return [self._normalize(x) for x in r]
            elif r:
                return [self._normalize(r)]
            else:
                return []

        except Fault as e:
            raise Exception(f"SOAP Error al buscar habitaciones: {e}")
