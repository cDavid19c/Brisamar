import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class ReservaSoap:
    """
    Cliente SOAP para consultar reservas.
    Equivalente al servicio buscarDatosReservaWS.asmx
    """

    def __init__(self):
        self.wsdl = "http://soapbrisamar.runasp.net/buscarDatosReservaWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    def _normalize(self, d):
        """Normaliza la respuesta SOAP"""
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idReserva": d.get("IdReserva"),
            "idHabitacion": d.get("IdHabitacion"),
            "idUsuario": d.get("IdUsuario"),
            "fechaInicio": fmt(d.get("FechaInicio")),
            "fechaFin": fmt(d.get("FechaFin")),
            "numeroHuespedes": d.get("NumeroHuespedes"),
            "estadoReserva": d.get("EstadoReserva"),
            "costoTotal": d.get("CostoTotal"),
            "fechaReserva": fmt(d.get("FechaReserva")),
            "nombreHabitacion": d.get("NombreHabitacion"),
            "nombreHotel": d.get("NombreHotel"),
            "nombreUsuario": d.get("NombreUsuario"),
            "apellidoUsuario": d.get("ApellidoUsuario"),
            "correoUsuario": d.get("CorreoUsuario"),
            "mensaje": d.get("Mensaje")
        }

    def buscar_reserva(self, id_reserva):
        """
        Consulta la información completa de una reserva existente.
        
        Parámetros:
            id_reserva (int): ID de la reserva (obligatorio)
            
        Retorna:
            Diccionario con todos los datos de la reserva
        """
        
        if not id_reserva or id_reserva <= 0:
            raise ValueError("Debe indicar un id_reserva válido (> 0).")

        try:
            # Llamada SOAP
            r = self.client.service.BuscarDatosReserva(id_reserva)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al buscar reserva: {e}")
