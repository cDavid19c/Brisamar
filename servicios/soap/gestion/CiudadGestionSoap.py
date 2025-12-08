import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class CiudadGestionSoap:

    def __init__(self):
        # WSDL PUBLICADO EN AZURE 🚀
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/CiudadService.asmx.asmx?wsdl"
        )

        # Desactivar SSL (Azure usa certificado intermedio)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =====================================================
    #     NORMALIZACIÓN → Igual a REST
    # =====================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdCiudad": d.get("IdCiudad"),
            "IdPais": d.get("IdPais"),
            "NombreCiudad": d.get("NombreCiudad"),
            "EstadoCiudad": d.get("EstadoCiudad"),
            "FechaModificacionCiudad": (
                d.get("FechaModificacionCiudad").isoformat()
                if d.get("FechaModificacionCiudad") else None
            )
        }

    # =====================================================
    #     LISTAR
    # =====================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerCiudad()
            result = serialize_object(result)
            return [self._normalize(item) for item in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar ciudades: {e}")
    
    def obtener_ciudades(self):
        return self.listar()

    # =====================================================
    #     OBTENER POR ID
    # =====================================================
    def obtener_por_id(self, id_ciudad):
        try:
            result = self.client.service.ObtenerCiudadPorId(id_ciudad)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener ciudad {id_ciudad}: {e}")
    
    def obtener_ciudad_por_id(self, id_ciudad):
        return self.obtener_por_id(id_ciudad)

    # =====================================================
    #     CREAR
    # =====================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearCiudad(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear ciudad: {e}")

    # =====================================================
    #     ACTUALIZAR
    # =====================================================
    def actualizar(self, id_ciudad, dto):
        try:
            result = self.client.service.ActualizarCiudad(id_ciudad, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar ciudad {id_ciudad}: {e}")

    # =====================================================
    #     ELIMINAR
    # =====================================================
    def eliminar(self, id_ciudad):
        try:
            return self.client.service.EliminarCiudad(id_ciudad)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar ciudad {id_ciudad}: {e}")

    # =====================================================
    #     ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # =====================================================
    def crear_ciudad(self, id_ciudad: int, id_pais: int, nombre: str, estado: bool = True):
        dto = {
            "IdCiudad": id_ciudad,
            "IdPais": id_pais,
            "NombreCiudad": nombre,
            "EstadoCiudad": estado,
            "FechaModificacionCiudad": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_ciudad(self, id_ciudad: int, id_pais: int, nombre: str, estado: bool = True):
        dto = {
            "IdCiudad": id_ciudad,
            "IdPais": id_pais,
            "NombreCiudad": nombre,
            "EstadoCiudad": estado,
            "FechaModificacionCiudad": datetime.now().isoformat()
        }
        return self.actualizar(id_ciudad, dto)
    
    def eliminar_ciudad(self, id_ciudad: int):
        return self.eliminar(id_ciudad)
