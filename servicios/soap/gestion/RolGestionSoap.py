import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault

class RolGestionSoap:

    def __init__(self):
        # URL DEL WSDL
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/RolWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        # Cliente SOAP
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ---------------------------------------------
    # Normalización de SOAP → dict
    # ---------------------------------------------
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "IdRol": d.get("IdRol"),
            "NombreRol": d.get("NombreRol"),
            "EstadoRol": d.get("EstadoRol"),
            "FechaModificacionRol": fmt(d.get("FechaModificacionRol")),
        }

    # ---------------------------------------------
    # LISTAR
    # ---------------------------------------------
    def listar(self):
        try:
            # ObtenerRol devuelve directamente una lista
            r = self.client.service.ObtenerRol()
            if r is None:
                return []
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar roles: {e}")
        except Exception as e:
            raise Exception(f"Error al listar roles: {e}")
    
    def obtener_roles(self):
        return self.listar()
    
    def obtener_rol_por_id(self, id_rol):
        return self.obtener_por_id(id_rol)

    # ---------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------
    def obtener_por_id(self, id_rol):
        try:
            r = self.client.service.ObtenerRolPorId(id_rol)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener rol por ID: {e}")

    # ---------------------------------------------
    # CREAR
    # ---------------------------------------------
    def crear(self, dto):
        try:
            r = self.client.service.CrearRol(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear rol: {e}")

    # ---------------------------------------------
    # ACTUALIZAR
    # ---------------------------------------------
    def actualizar(self, id_rol, dto):
        try:
            r = self.client.service.ActualizarRol(id_rol, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar rol: {e}")

    # ---------------------------------------------
    # ELIMINAR
    # ---------------------------------------------
    def eliminar(self, id_rol):
        try:
            return self.client.service.EliminarRol(id_rol)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar rol: {e}")

    # ---------------------------------------------
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ---------------------------------------------
    def crear_rol(self, dto):
        """Alias para crear() - recibe un DTO directamente"""
        return self.crear(dto)
    
    def actualizar_rol(self, id_rol, dto):
        """Alias para actualizar() - recibe id y DTO"""
        return self.actualizar(id_rol, dto)
    
    def eliminar_rol(self, id_rol):
        """Alias para eliminar()"""
        return self.eliminar(id_rol)
