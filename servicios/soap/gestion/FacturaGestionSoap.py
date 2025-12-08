import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault

class FacturaGestionSoap:

    def __init__(self):
        # WSDL PUBLICADO EN AZURE
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/FacturaWS.asmx?wsdl"
        )

        # Desactivar validación SSL (Azure)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ==========================================================
    # NORMALIZAR → Parámetros idénticos a REST
    # ==========================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdFactura": d.get("IdFactura"),
            "IdReserva": d.get("IdReserva"),
            "Subtotal": d.get("Subtotal"),
            "Descuento": d.get("Descuento"),
            "Impuesto": d.get("Impuesto"),
            "Total": d.get("Total"),
            "UrlPdf": d.get("UrlPdf"),
        }

    # ==========================================================
    # LISTAR FACTURAS
    # ==========================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerFacturas()
            result = serialize_object(result)
            return [self._normalize(item) for item in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar facturas: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_facturas(self):
        return self.listar()

    # ==========================================================
    # OBTENER POR ID
    # ==========================================================
    def obtener_por_id(self, id_factura):
        try:
            result = self.client.service.ObtenerFacturaPorId(id_factura)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener factura {id_factura}: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_factura_por_id(self, id_factura):
        return self.obtener_por_id(id_factura)

    # ==========================================================
    # CREAR FACTURA
    # ==========================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearFactura(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear factura: {e}")

    # ==========================================================
    # ACTUALIZAR FACTURA
    # ==========================================================
    def actualizar(self, id_factura, dto):
        try:
            result = self.client.service.ActualizarFactura(id_factura, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar factura {id_factura}: {e}")

    # ==========================================================
    # ELIMINAR FACTURA
    # ==========================================================
    def eliminar(self, id_factura):
        try:
            return self.client.service.EliminarFactura(id_factura)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar factura {id_factura}: {e}")

    # ==========================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ==========================================================
    def crear_factura(self, id_reserva, subtotal, descuento, impuesto, total, url_pdf=""):
        dto = {
            "IdReserva": id_reserva,
            "Subtotal": subtotal,
            "Descuento": descuento,
            "Impuesto": impuesto,
            "Total": total,
            "UrlPdf": url_pdf
        }
        return self.crear(dto)
    
    def actualizar_factura(self, id_factura, id_reserva, subtotal, descuento, impuesto, total, url_pdf=""):
        dto = {
            "IdFactura": id_factura,
            "IdReserva": id_reserva,
            "Subtotal": subtotal,
            "Descuento": descuento,
            "Impuesto": impuesto,
            "Total": total,
            "UrlPdf": url_pdf
        }
        return self.actualizar(id_factura, dto)
    
    def eliminar_factura(self, id_factura):
        return self.eliminar(id_factura)
