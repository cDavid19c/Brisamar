import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime

class AmenidadGestionSoap:

    def __init__(self):
        self.wsdl = "http://brisamargs.runasp.net/AmenidadWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # -----------------------------
    # NORMALIZADOR
    # -----------------------------
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdAmenidad": d.get("IdAmenidad"),
            "NombreAmenidad": d.get("NombreAmenidad"),
            "EstadoAmenidad": d.get("EstadoAmenidad"),
            "FechaModificacionAmenidad": (
                d.get("FechaModificacionAmenidad").isoformat()
                if d.get("FechaModificacionAmenidad") else None
            )
        }

    # -----------------------------
    # LISTAR
    # -----------------------------
    def listar(self):
        try:
            data = self.client.service.ObtenerAmenidades()
            data = serialize_object(data)
            return [self._normalize(item) for item in data]
        except Fault as e:
            raise Exception(f"Error SOAP al listar amenidades: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_amenidades(self):
        return self.listar()

    # -----------------------------
    # OBTENER
    # -----------------------------
    def obtener_por_id(self, id_amenidad):
        try:
            result = self.client.service.ObtenerAmenidadPorId(id_amenidad)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener amenidad {id_amenidad}: {e}")
    
    def obtener_amenidad_por_id(self, id_amenidad):
        return self.obtener_por_id(id_amenidad)

    # -----------------------------
    # CREAR
    # -----------------------------
    def crear(self, dto):
        try:
            result = self.client.service.CrearAmenidad(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear amenidad: {e}")

    # -----------------------------
    # ACTUALIZAR
    # -----------------------------
    def actualizar(self, id_amenidad, dto):
        try:
            result = self.client.service.ActualizarAmenidad(id_amenidad, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar amenidad {id_amenidad}: {e}")

    # -----------------------------
    # ELIMINAR
    # -----------------------------
    def eliminar(self, id_amenidad):
        try:
            return self.client.service.EliminarAmenidad(id_amenidad)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar amenidad {id_amenidad}: {e}")

    # =============================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # =============================
    def crear_amenidad(self, id_amenidad: int, nombre: str, estado: bool = True):
        """Alias para crear() - convierte parámetros a DTO"""
        dto = {
            "IdAmenidad": id_amenidad,
            "NombreAmenidad": nombre,
            "EstadoAmenidad": estado,
            "FechaModificacionAmenidad": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_amenidad(self, id_amenidad: int, nombre: str, estado: bool = True):
        """Alias para actualizar() - convierte parámetros a DTO"""
        dto = {
            "IdAmenidad": id_amenidad,
            "NombreAmenidad": nombre,
            "EstadoAmenidad": estado,
            "FechaModificacionAmenidad": datetime.now().isoformat()
        }
        return self.actualizar(id_amenidad, dto)
    
    def eliminar_amenidad(self, id_amenidad: int):
        """Alias para eliminar()"""
        return self.eliminar(id_amenidad)
