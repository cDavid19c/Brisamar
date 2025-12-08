import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HoldGestionSoap:

    def __init__(self):
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/HoldWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ================= NORMALIZAR DATOS =====================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "IdHold": d.get("IdHold"),
            "IdHabitacion": d.get("IdHabitacion"),
            "IdReserva": d.get("IdReserva"),
            "TiempoHold": d.get("TiempoHold"),
            "FechaInicioHold": fmt(d.get("FechaInicioHold")),
            "FechaFinalHold": fmt(d.get("FechaFinalHold")),
            "EstadoHold": d.get("EstadoHold"),
        }

    # ================= LISTAR =====================
    def listar(self):
        try:
            r = self.client.service.ObtenerHold()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"Error SOAP al listar Hold: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_hold(self):
        return self.listar()

    # ================= OBTENER POR ID =====================
    def obtener_por_id(self, id_hold):
        try:
            r = self.client.service.ObtenerHoldPorId(id_hold)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener Hold {id_hold}: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_hold_por_id(self, id_hold):
        return self.obtener_por_id(id_hold)

    # ================= CREAR =====================
    def crear(self, dto):
        try:
            r = self.client.service.CrearHold(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al crear Hold: {e}")

    # ================= ACTUALIZAR =====================
    def actualizar(self, id_hold, dto):
        try:
            r = self.client.service.ActualizarHold(id_hold, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar Hold {id_hold}: {e}")

    # ================= ELIMINAR =====================
    def eliminar(self, id_hold):
        try:
            return self.client.service.EliminarHold(id_hold)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar Hold {id_hold}: {e}")

    # ================= ALIAS PARA COMPATIBILIDAD =====================
    def crear_hold(self, id_habitacion, id_reserva, tiempo_hold, fecha_inicio, fecha_final, estado=True):
        dto = {
            "IdHabitacion": id_habitacion,
            "IdReserva": id_reserva,
            "TiempoHold": tiempo_hold,
            "FechaInicioHold": fecha_inicio,
            "FechaFinalHold": fecha_final,
            "EstadoHold": estado
        }
        return self.crear(dto)
    
    def actualizar_hold(self, id_hold, id_habitacion, id_reserva, tiempo_hold, fecha_inicio, fecha_final, estado=True):
        dto = {
            "IdHold": id_hold,
            "IdHabitacion": id_habitacion,
            "IdReserva": id_reserva,
            "TiempoHold": tiempo_hold,
            "FechaInicioHold": fecha_inicio,
            "FechaFinalHold": fecha_final,
            "EstadoHold": estado
        }
        return self.actualizar(id_hold, dto)
    
    def eliminar_hold(self, id_hold):
        return self.eliminar(id_hold)
