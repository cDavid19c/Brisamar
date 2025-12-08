import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class AmexHabGestionSoap:

    def __init__(self):
        # Cambia el puerto si tu SOAP usa otro
        self.wsdl = "http://allpahousenycgs.runasp.net/AmexHabWS.asmx?wsdl"

        # Desactivar verificación SSL porque es localhost
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # -----------------------------------------
    # NORMALIZADOR — Igual que REST
    # -----------------------------------------
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdHabitacion": d.get("IdHabitacion"),
            "IdAmenidad": d.get("IdAmenidad"),
            "EstadoAmexHab": d.get("EstadoAmexHab"),
            "FechaModificacionAmexHab": (
                d.get("FechaModificacionAmexHab").isoformat()
                if d.get("FechaModificacionAmexHab") else None
            )
        }

    # -----------------------------------------
    # LISTAR
    # -----------------------------------------
    def listar(self):
        try:
            data = self.client.service.ObtenerAmexHab()
            data = serialize_object(data)
            return [self._normalize(item) for item in data]
        except Fault as e:
            raise Exception(f"Error SOAP al listar AMEXHAB: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_amexhab(self):
        return self.listar()

    # -----------------------------------------
    # OBTENER POR ID COMPUESTO
    # -----------------------------------------
    def obtener_por_id(self, id_habitacion, id_amenidad):
        try:
            result = self.client.service.ObtenerAmexHabPorId(id_habitacion, id_amenidad)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener AmexHab: {e}")
    
    def obtener_amexhab_por_id(self, id_habitacion, id_amenidad):
        return self.obtener_por_id(id_habitacion, id_amenidad)

    # -----------------------------------------
    # CREAR
    # -----------------------------------------
    def crear(self, dto):
        try:
            result = self.client.service.CrearAmexHab(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear AmexHab: {e}")

    # -----------------------------------------
    # ACTUALIZAR
    # -----------------------------------------
    def actualizar(self, dto):
        try:
            result = self.client.service.ActualizarAmexHab(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar AmexHab: {e}")

    # -----------------------------------------
    # ELIMINAR
    # -----------------------------------------
    def eliminar(self, id_habitacion, id_amenidad):
        try:
            return self.client.service.EliminarAmexHab(id_habitacion, id_amenidad)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar AmexHab: {e}")

    # -----------------------------------------
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # -----------------------------------------
    def crear_amexhab(self, id_habitacion, id_amenidad, estado=True):
        dto = {
            "IdHabitacion": id_habitacion,
            "IdAmenidad": id_amenidad,
            "EstadoAmexHab": estado,
            "FechaModificacionAmexHab": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_amexhab(self, id_habitacion, id_amenidad, estado=True):
        dto = {
            "IdHabitacion": id_habitacion,
            "IdAmenidad": id_amenidad,
            "EstadoAmexHab": estado,
            "FechaModificacionAmexHab": datetime.now().isoformat()
        }
        return self.actualizar(dto)
    
    def eliminar_amexhab(self, id_habitacion, id_amenidad):
        return self.eliminar(id_habitacion, id_amenidad)
