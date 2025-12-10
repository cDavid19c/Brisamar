import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PaisGestionSoap:

    def __init__(self):
        # 👉 Asegúrate de que el link sea exactamente este:
        self.wsdl = (
            "http://brisamargs.runasp.net/PaisWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # Normalizador de respuesta SOAP → dict
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "IdPais": d.get("IdPais"),
            "NombrePais": d.get("NombrePais"),
            "EstadoPais": d.get("EstadoPais"),
            "FechaModificacionPais": fmt(d.get("FechaModificacionPais")),
        }

    # ========================================================
    # LISTAR PAISES
    # ========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerPais()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar países: {e}")
    
    def obtener_paises(self):
        return self.listar()
    
    def obtener_pais_por_id(self, id_pais):
        return self.obtener_por_id(id_pais)

    # ========================================================
    # OBTENER POR ID
    # ========================================================
    def obtener_por_id(self, id_pais):
        try:
            r = self.client.service.ObtenerPaisPorId(id_pais)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener país por ID: {e}")

    # ========================================================
    # CREAR PAÍS
    # ========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearPais(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear país: {e}")

    # ========================================================
    # ACTUALIZAR PAÍS
    # ========================================================
    def actualizar(self, id_pais, dto):
        try:
            r = self.client.service.ActualizarPais(id_pais, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar país: {e}")

    # ========================================================
    # ELIMINAR PAÍS (LÓGICO)
    # ========================================================
    def eliminar(self, id_pais):
        try:
            return self.client.service.EliminarPais(id_pais)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar país: {e}")

    # ========================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ========================================================
    def crear_pais(self, id_pais: int, nombre: str, estado: bool = True):
        dto = {
            "IdPais": id_pais,
            "NombrePais": nombre,
            "EstadoPais": estado,
            "FechaModificacionPais": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_pais(self, id_pais: int, nombre: str, estado: bool = True):
        dto = {
            "IdPais": id_pais,
            "NombrePais": nombre,
            "EstadoPais": estado,
            "FechaModificacionPais": datetime.now().isoformat()
        }
        return self.actualizar(id_pais, dto)
    
    def eliminar_pais(self, id_pais: int):
        return self.eliminar(id_pais)
