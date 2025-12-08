import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class ReservaGestionSoap:

    def __init__(self):
        # 👉 LINK DEL WSDL SOAP
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/ReservaWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ============================================================
    # Normalización SOAP → dict
    # ============================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "IdReserva": d.get("IdReserva"),
            "IdUnicoUsuario": d.get("IdUnicoUsuario"),
            "IdUnicoUsuarioExterno": d.get("IdUnicoUsuarioExterno"),
            "CostoTotalReserva": d.get("CostoTotalReserva"),
            "FechaRegistroReserva": fmt(d.get("FechaRegistroReserva")),
            "FechaInicioReserva": fmt(d.get("FechaInicioReserva")),
            "FechaFinalReserva": fmt(d.get("FechaFinalReserva")),
            "EstadoGeneralReserva": d.get("EstadoGeneralReserva"),
            "EstadoReserva": d.get("EstadoReserva"),
            "FechaModificacionReserva": fmt(d.get("FechaModificacionReserva")),
        }

    # ============================================================
    # LISTAR RESERVAS
    # ============================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerReservas()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar reservas: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_reservas(self):
        return self.listar()

    # ============================================================
    # OBTENER POR ID
    # ============================================================
    def obtener_por_id(self, id_reserva):
        try:
            r = self.client.service.ObtenerReservaPorId(id_reserva)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener reserva por ID: {e}")
    
    def obtener_reserva_por_id(self, id_reserva):
        return self.obtener_por_id(id_reserva)

    # ============================================================
    # CREAR RESERVA
    # ============================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearReserva(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear reserva: {e}")

    # ============================================================
    # ACTUALIZAR RESERVA
    # ============================================================
    def actualizar(self, id_reserva, dto):
        try:
            r = self.client.service.ActualizarReserva(id_reserva, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar reserva: {e}")

    # ============================================================
    # ELIMINAR (CANCELAR) RESERVA
    # ============================================================
    def eliminar(self, id_reserva):
        try:
            return self.client.service.EliminarReserva(id_reserva)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar reserva: {e}")

    # ============================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ============================================================
    def crear_reserva(self, dto):
        """Alias para crear() - recibe un DTO directamente"""
        return self.crear(dto)
    
    def actualizar_reserva(self, id_reserva, dto):
        """Alias para actualizar() - recibe id y DTO"""
        return self.actualizar(id_reserva, dto)
    
    def eliminar_reserva(self, id_reserva):
        """Alias para eliminar()"""
        return self.eliminar(id_reserva)
