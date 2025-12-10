import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class MetodoPagoGestionSoap:

    def __init__(self):
        # 👉 Asegúrate de reemplazar por el WSDL verdadero una vez publicado:
        self.wsdl = (
            "http://brisamargs.runasp.net/MetodoPagoWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)

        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ========================================================
    # Normalización de respuesta SOAP → dict Python
    # ========================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(x):
            return x.isoformat() if x else None

        return {
            "IdMetodoPago": d.get("IdMetodoPago"),
            "NombreMetodoPago": d.get("NombreMetodoPago"),
            "EstadoMetodoPago": d.get("EstadoMetodoPago"),
            "FechaModificacionMetodoPago": fmt(d.get("FechaModificacionMetodoPago")),
        }

    # ========================================================
    # LISTAR MÉTODOS DE PAGO
    # ========================================================
    def listar(self):
        try:
            r = self.client.service.ObtenerMetodoPago()
            r = serialize_object(r)
            return [self._normalize(x) for x in r]
        except Fault as e:
            raise Exception(f"SOAP Error al listar métodos de pago: {e}")
    
    def obtener_metodos_pago(self):
        return self.listar()
    
    def obtener_metodo_pago_por_id(self, id_metodo):
        return self.obtener_por_id(id_metodo)

    # ========================================================
    # OBTENER POR ID
    # ========================================================
    def obtener_por_id(self, id_metodo):
        try:
            r = self.client.service.ObtenerMetodoPagoPorId(id_metodo)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al obtener método por ID: {e}")

    # ========================================================
    # CREAR MÉTODO DE PAGO
    # ========================================================
    def crear(self, dto):
        try:
            r = self.client.service.CrearMetodoPago(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear método de pago: {e}")

    # ========================================================
    # ACTUALIZAR MÉTODO DE PAGO
    # ========================================================
    def actualizar(self, id_metodo, dto):
        try:
            r = self.client.service.ActualizarMetodoPago(id_metodo, dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al actualizar método de pago: {e}")

    # ========================================================
    # ELIMINAR MÉTODO DE PAGO (LÓGICO)
    # ========================================================
    def eliminar(self, id_metodo):
        try:
            return self.client.service.EliminarMetodoPago(id_metodo)
        except Fault as e:
            raise Exception(f"SOAP Error al eliminar método de pago: {e}")

    # ========================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ========================================================
    def crear_metodo_pago(self, id_metodo: int, nombre_metodo: str, estado_metodo: bool = True):
        """Alias para crear() - convierte parámetros a DTO"""
        dto = {
            "IdMetodoPago": id_metodo,
            "NombreMetodoPago": nombre_metodo,
            "EstadoMetodoPago": estado_metodo,
            "FechaModificacionMetodoPago": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_metodo_pago(self, id_metodo: int, nombre_metodo: str, estado_metodo: bool = True):
        """Alias para actualizar() - convierte parámetros a DTO"""
        dto = {
            "IdMetodoPago": id_metodo,
            "NombreMetodoPago": nombre_metodo,
            "EstadoMetodoPago": estado_metodo,
            "FechaModificacionMetodoPago": datetime.now().isoformat()
        }
        return self.actualizar(id_metodo, dto)
    
    def eliminar_metodo_pago(self, id_metodo: int):
        """Alias para eliminar()"""
        return self.eliminar(id_metodo)
