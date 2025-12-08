import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault

class DescuentoGestionSoap:

    def __init__(self):
        # Cambia el puerto si tu SOAP usa otro
        self.wsdl = "http://allpahousenycgs.runasp.net/DescuentoWS.asmx?wsdl"

        # Desactivar SSL (IIS Express usa certificado auto-firmado)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ---------------------------------------------------------
    # NORMALIZACIÓN (SOAP → JSON REST)
    # ---------------------------------------------------------
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdDescuento": d.get("IdDescuento"),
            "NombreDescuento": d.get("NombreDescuento"),
            "ValorDescuento": float(d.get("ValorDescuento")) if d.get("ValorDescuento") is not None else None,
            "FechaInicioDescuento": (
                d.get("FechaInicioDescuento").isoformat()
                if d.get("FechaInicioDescuento") else None
            ),
            "FechaFinDescuento": (
                d.get("FechaFinDescuento").isoformat()
                if d.get("FechaFinDescuento") else None
            ),
            "EstadoDescuento": d.get("EstadoDescuento"),
            "FechaModificacionDescuento": (
                d.get("FechaModificacionDescuento").isoformat()
                if d.get("FechaModificacionDescuento") else None
            )
        }

    # ---------------------------------------------------------
    # LISTAR DESCUENTOS
    # ---------------------------------------------------------
    def listar(self):
        try:
            data = self.client.service.ObtenerDescuentos()
            data = serialize_object(data)
            return [self._normalize(item) for item in data]

        except Fault as e:
            raise Exception(f"Error SOAP al listar descuentos: {e}")
    
    def obtener_descuentos(self):
        return self.listar()
    
    def obtener_descuento_por_id(self, id_descuento):
        return self.obtener_por_id(id_descuento)

    # ---------------------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------------------
    def obtener_por_id(self, id_descuento):
        try:
            res = self.client.service.ObtenerDescuentoPorId(id_descuento)
            return self._normalize(res)

        except Fault as e:
            raise Exception(f"Error SOAP al obtener descuento {id_descuento}: {e}")

    # ---------------------------------------------------------
    # CREAR DESCUENTO
    # ---------------------------------------------------------
    def crear(self, dto):
        try:
            result = self.client.service.CrearDescuento(dto)
            return self._normalize(result)

        except Fault as e:
            raise Exception(f"Error SOAP al crear descuento: {e}")

    # ---------------------------------------------------------
    # ACTUALIZAR DESCUENTO
    # ---------------------------------------------------------
    def actualizar(self, id_descuento, dto):
        try:
            result = self.client.service.ActualizarDescuento(id_descuento, dto)
            return self._normalize(result)

        except Fault as e:
            raise Exception(f"Error SOAP al actualizar descuento {id_descuento}: {e}")

    # ---------------------------------------------------------
    # ELIMINAR DESCUENTO
    # ---------------------------------------------------------
    def eliminar(self, id_descuento):
        try:
            return self.client.service.EliminarDescuento(id_descuento)

        except Fault as e:
            raise Exception(f"Error SOAP al eliminar descuento {id_descuento}: {e}")

    # ---------------------------------------------------------
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ---------------------------------------------------------
    def crear_descuento(self, id_descuento: int, nombre: str, valor: float, fecha_inicio: str, fecha_fin: str, estado: bool = True):
        dto = {
            "IdDescuento": id_descuento,
            "NombreDescuento": nombre,
            "ValorDescuento": valor,
            "FechaInicioDescuento": fecha_inicio,
            "FechaFinDescuento": fecha_fin,
            "EstadoDescuento": estado,
            "FechaModificacionDescuento": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_descuento(self, id_descuento: int, nombre: str, valor: float, fecha_inicio: str, fecha_fin: str, estado: bool = True):
        dto = {
            "IdDescuento": id_descuento,
            "NombreDescuento": nombre,
            "ValorDescuento": valor,
            "FechaInicioDescuento": fecha_inicio,
            "FechaFinDescuento": fecha_fin,
            "EstadoDescuento": estado,
            "FechaModificacionDescuento": datetime.now().isoformat()
        }
        return self.actualizar(id_descuento, dto)
    
    def eliminar_descuento(self, id_descuento: int):
        return self.eliminar(id_descuento)
