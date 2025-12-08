import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class TipoHabitacionGestionSoap:

    def __init__(self):
        # URL WSDL del servicio SOAP publicado en Azure
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/TipoHabitacionWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # NORMALIZADOR
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "IdTipoHabitacion": d.get("IdTipoHabitacion"),
            "NombreHabitacion": d.get("NombreHabitacion"),
            "EstadoTipoHabitacion": d.get("EstadoTipoHabitacion"),
            "FechaModificacionTipoHabitacion": fmt(d.get("FechaModificacionTipoHabitacion")),
        }

    # ========================================================
    # LISTAR
    # ========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerTiposHabitacion()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar tipos: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_tipos(self):
        return self.listar()

    # ========================================================
    # OBTENER POR ID
    # ========================================================
    def obtener_por_id(self, id_tipo):
        try:
            r = self.client.service.ObtenerTipoHabitacionPorId(id_tipo)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener tipo por ID: {e}")
    
    def obtener_tipo_por_id(self, id_tipo):
        return self.obtener_por_id(id_tipo)

    # ========================================================
    # CREAR
    # ========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearTipoHabitacion(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear tipo habitación: {e}")

    # ========================================================
    # ACTUALIZAR
    # ========================================================
    def actualizar(self, id_tipo, dto):
        try:
            r = self.client.service.ActualizarTipoHabitacion(id_tipo, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar tipo habitación: {e}")

    # ========================================================
    # ELIMINAR
    # ========================================================
    def eliminar(self, id_tipo):
        try:
            return self.client.service.EliminarTipoHabitacion(id_tipo)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar tipo habitación: {e}")

    # ========================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ========================================================
    def crear_tipo(self, dto):
        """Alias para crear() - recibe un DTO directamente"""
        return self.crear(dto)
    
    def actualizar_tipo(self, id_tipo, dto):
        """Alias para actualizar() - recibe id y DTO"""
        return self.actualizar(id_tipo, dto)
    
    def eliminar_tipo(self, id_tipo):
        """Alias para eliminar()"""
        return self.eliminar(id_tipo)
