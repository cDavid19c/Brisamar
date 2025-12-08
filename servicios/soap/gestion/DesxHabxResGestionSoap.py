import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class DesxHabxResGestionSoap:

    def __init__(self):
        # 🔥 WSDL PUBLICADO EN AZURE
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/DesxHabxResWS.asmx?wsdl"
        )

        # Desactivar SSL (Azure usa certificado intermedio)
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =====================================================
    # NORMALIZADOR → MISMO FORMATO QUE REST
    # =====================================================
    def _normalize(self, item):
        if item is None:
            return None

        d = serialize_object(item)

        return {
            "IdDescuento": d.get("IdDescuento"),
            "IdHabxRes": d.get("IdHabxRes"),
            "MontoDesxHabxRes": d.get("MontoDesxHabxRes"),
            "EstadoDesxHabxRes": d.get("EstadoDesxHabxRes"),
            "FechaModificacionDesxHabxRes": (
                d.get("FechaModificacionDesxHabxRes").isoformat()
                if d.get("FechaModificacionDesxHabxRes") else None
            )
        }

    # =====================================================
    # LISTAR
    # =====================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerDesxHabxRes()
            result = serialize_object(result)
            return [self._normalize(item) for item in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar DesxHabxRes: {e}")
    
    def obtener_desxhabxres(self):
        return self.listar()
    
    def obtener_desxhabxres_por_id(self, id_descuento, id_habxres):
        return self.obtener_por_id(id_descuento, id_habxres)

    # =====================================================
    # OBTENER POR ID COMPUESTO
    # =====================================================
    def obtener_por_id(self, id_descuento, id_habxres):
        try:
            result = self.client.service.ObtenerDesxHabxResPorId(id_descuento, id_habxres)
            return self._normalize(result)
        except Fault as e:
            raise Exception(
                f"Error SOAP al obtener DesxHabxRes ({id_descuento}, {id_habxres}): {e}"
            )

    # =====================================================
    # CREAR
    # =====================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearDesxHabxRes(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear DesxHabxRes: {e}")

    # =====================================================
    # ACTUALIZAR
    # =====================================================
    def actualizar(self, dto):
        try:
            result = self.client.service.ActualizarDesxHabxRes(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(
                f"Error SOAP al actualizar DesxHabxRes ({dto.get('IdDescuento')}, {dto.get('IdHabxRes')}): {e}"
            )

    # =====================================================
    # ELIMINAR
    # =====================================================
    def eliminar(self, id_descuento, id_habxres):
        try:
            return self.client.service.EliminarDesxHabxRes(id_descuento, id_habxres)
        except Fault as e:
            raise Exception(
                f"Error SOAP al eliminar DesxHabxRes ({id_descuento}, {id_habxres}): {e}"
            )

    # =====================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # =====================================================
    def crear_desxhabxres(self, id_descuento, id_habxres, monto, estado=True):
        dto = {
            "IdDescuento": id_descuento,
            "IdHabxRes": id_habxres,
            "MontoDesxHabxRes": monto,
            "EstadoDesxHabxRes": estado,
            "FechaModificacionDesxHabxRes": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_desxhabxres(self, id_descuento, id_habxres, monto, estado=True):
        dto = {
            "IdDescuento": id_descuento,
            "IdHabxRes": id_habxres,
            "MontoDesxHabxRes": monto,
            "EstadoDesxHabxRes": estado,
            "FechaModificacionDesxHabxRes": datetime.now().isoformat()
        }
        return self.actualizar(dto)
    
    def eliminar_desxhabxres(self, id_descuento, id_habxres):
        return self.eliminar(id_descuento, id_habxres)
