import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HabxResGestionSoap:

    def __init__(self):
        # WSDL publicado en Azure
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/HabxResWS.asmx?wsdl"
        )

        # Azure → certificados intermedios, permitimos verify=False
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ==========================================================
    # NORMALIZACIÓN → deja igual que REST
    # ==========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "IdHabxRes": d.get("IdHabxRes"),
            "IdHabitacion": d.get("IdHabitacion"),
            "IdReserva": d.get("IdReserva"),
            "CapacidadReservaHabxRes": d.get("CapacidadReservaHabxRes"),
            "CostoCalculadoHabxRes": d.get("CostoCalculadoHabxRes"),
            "DescuentoHabxRes": d.get("DescuentoHabxRes"),
            "ImpuestosHabxRes": d.get("ImpuestosHabxRes"),
            "EstadoHabxRes": d.get("EstadoHabxRes"),
            "FechaModificacionHabxRes": fmt(d.get("FechaModificacionHabxRes"))
        }

    # ==========================================================
    # LISTAR
    # ==========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerHabxRes()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"Error SOAP al listar HabxRes: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_habxres(self):
        return self.listar()

    # ==========================================================
    # OBTENER POR ID
    # ==========================================================
    def obtener_por_id(self, id_habxres):
        try:
            r = self.client.service.ObtenerHabxResPorId(id_habxres)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener HabxRes {id_habxres}: {e}")

    # ==========================================================
    # CREAR
    # ==========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearHabxRes(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al crear HabxRes: {e}")

    # ==========================================================
    # ACTUALIZAR
    # ==========================================================
    def actualizar(self, id_habxres, dto):
        try:
            r = self.client.service.ActualizarHabxRes(id_habxres, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar HabxRes {id_habxres}: {e}")

    # ==========================================================
    # ELIMINAR
    # ==========================================================
    def eliminar(self, id_habxres):
        try:
            return self.client.service.EliminarHabxRes(id_habxres)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar HabxRes {id_habxres}: {e}")

    # ==========================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ==========================================================
    def obtener_habxres_por_id(self, id_habxres):
        return self.obtener_por_id(id_habxres)
    
    def crear_habxres(self, id_habitacion, id_reserva, capacidad, costo, descuento, impuestos, estado=True):
        dto = {
            "IdHabitacion": id_habitacion,
            "IdReserva": id_reserva,
            "CapacidadReservaHabxRes": capacidad,
            "CostoCalculadoHabxRes": costo,
            "DescuentoHabxRes": descuento,
            "ImpuestosHabxRes": impuestos,
            "EstadoHabxRes": estado,
            "FechaModificacionHabxRes": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_habxres(self, id_habxres, id_habitacion, id_reserva, capacidad, costo, descuento, impuestos, estado=True):
        dto = {
            "IdHabxRes": id_habxres,
            "IdHabitacion": id_habitacion,
            "IdReserva": id_reserva,
            "CapacidadReservaHabxRes": capacidad,
            "CostoCalculadoHabxRes": costo,
            "DescuentoHabxRes": descuento,
            "ImpuestosHabxRes": impuestos,
            "EstadoHabxRes": estado,
            "FechaModificacionHabxRes": datetime.now().isoformat()
        }
        return self.actualizar(id_habxres, dto)
    
    def eliminar_habxres(self, id_habxres):
        return self.eliminar(id_habxres)
