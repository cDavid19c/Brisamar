import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class FacturaSoap:
    """
    Cliente SOAP para emitir facturas.
    Equivalente al servicio EmitirFacturaHotelWS.asmx
    """

    def __init__(self):
        self.wsdl = "http://soapbrisamar.runasp.net/EmitirFacturaHotelWS.asmx?wsdl"

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
            "idFactura": d.get("IdFactura"),
            "idReserva": d.get("IdReserva"),
            "numeroFactura": d.get("NumeroFactura"),
            "fechaEmision": fmt(d.get("FechaEmision")),
            "subtotal": d.get("Subtotal"),
            "impuestos": d.get("Impuestos"),
            "descuentos": d.get("Descuentos"),
            "total": d.get("Total"),
            "correo": d.get("Correo"),
            "urlFactura": d.get("UrlFactura"),
            "estado": d.get("Estado"),
            "mensaje": d.get("Mensaje"),
            "nombreCliente": d.get("NombreCliente"),
            "apellidoCliente": d.get("ApellidoCliente")
        }

    def emitir_factura(self, id_reserva, correo=None, url_factura=None):
        """
        Emite una factura para una reserva.
        
        Parámetros:
            id_reserva (int): ID de la reserva (obligatorio)
            correo (str, optional): Correo electrónico para enviar la factura
            url_factura (str, optional): URL del PDF de la factura
            
        Retorna:
            Diccionario con los datos de la factura emitida
        """
        
        # Validaciones
        if id_reserva is None or id_reserva <= 0:
            raise ValueError("El campo 'id_reserva' debe ser mayor que 0.")

        try:
            # Preparar DTO para SOAP
            dto = {
                "IdReserva": id_reserva,
                "Correo": correo,
                "UrlFactura": url_factura
            }

            # Llamada SOAP
            r = self.client.service.EmitirFactura(dto)
            return self._normalize(r)

        except Fault as e:
            raise Exception(f"SOAP Error al emitir factura: {e}")
