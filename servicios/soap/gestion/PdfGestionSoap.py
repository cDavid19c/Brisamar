import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PdfGestionSoap:

    def __init__(self):
        # 👉 LINK DEL WSDL SOAP
        self.wsdl = (
            "http://brisamargs.runasp.net/PdfWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ---------------------------------------------------------
    # Normalización SOAP → dict
    # ---------------------------------------------------------
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "IdPdf": d.get("IdPdf"),
            "IdFactura": d.get("IdFactura"),
            "UrlPdf": d.get("UrlPdf"),
            "EstadoPdf": d.get("EstadoPdf"),
            "FechaModificacionPdf": fmt(d.get("FechaModificacionPdf")),
        }

    # ---------------------------------------------------------
    # LISTAR PDF
    # ---------------------------------------------------------
    def listar(self):
        try:
            r = self.client.service.ObtenerPdf()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar PDFs: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_pdfs(self):
        return self.listar()

    # ---------------------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------------------
    def obtener_por_id(self, id_pdf):
        try:
            r = self.client.service.ObtenerPdfPorId(id_pdf)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener PDF por ID: {e}")
    
    def obtener_pdf_por_id(self, id_pdf):
        return self.obtener_por_id(id_pdf)

    # ---------------------------------------------------------
    # CREAR PDF
    # ---------------------------------------------------------
    def crear(self, dto):
        try:
            r = self.client.service.CrearPdf(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear PDF: {e}")

    # ---------------------------------------------------------
    # ACTUALIZAR PDF
    # ---------------------------------------------------------
    def actualizar(self, id_pdf, dto):
        try:
            r = self.client.service.ActualizarPdf(id_pdf, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar PDF: {e}")

    # ---------------------------------------------------------
    # ELIMINAR PDF (LÓGICO)
    # ---------------------------------------------------------
    def eliminar(self, id_pdf):
        try:
            return self.client.service.EliminarPdf(id_pdf)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar PDF: {e}")

    # ---------------------------------------------------------
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ---------------------------------------------------------
    def crear_pdf(self, id_factura, url_pdf, estado=True):
        dto = {
            "IdFactura": id_factura,
            "UrlPdf": url_pdf,
            "EstadoPdf": estado,
            "FechaModificacionPdf": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_pdf(self, id_pdf, id_factura, url_pdf, estado=True):
        dto = {
            "IdPdf": id_pdf,
            "IdFactura": id_factura,
            "UrlPdf": url_pdf,
            "EstadoPdf": estado,
            "FechaModificacionPdf": datetime.now().isoformat()
        }
        return self.actualizar(id_pdf, dto)
    
    def eliminar_pdf(self, id_pdf):
        return self.eliminar(id_pdf)
