import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class PagoGestionSoap:

    def __init__(self):
        # 👉 WSDL publicado de PagoWS (ajústalo si tu URL cambia)
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/PagoWS.asmx?wsdl"
        )

        # Azure → requiere desactivar verificación SSL
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # ===============================================================
    # NORMALIZADOR → que coincida con REST EXACTAMENTE
    # ===============================================================
    def _normalize(self, p):
        if p is None:
            return None

        d = serialize_object(p)

        return {
            "idPago": d.get("IdPago"),
            "idMetodoPago": d.get("IdMetodoPago"),
            "idUnicoUsuarioExterno": d.get("IdUnicoUsuarioExterno"),
            "idUnicoUsuario": d.get("IdUnicoUsuario"),
            "idFactura": d.get("IdFactura"),
            "cuentaOrigenPago": d.get("CuentaOrigenPago"),
            "cuentaDestinoPago": d.get("CuentaDestinoPago"),
            "montoTotalPago": d.get("MontoTotalPago"),

            "fechaEmisionPago": (
                d.get("FechaEmisionPago").isoformat()
                if d.get("FechaEmisionPago") else None
            ),

            "estadoPago": d.get("EstadoPago"),

            "fechaModificacionPago": (
                d.get("FechaModificacionPago").isoformat()
                if d.get("FechaModificacionPago") else None
            )
        }

    # ===============================================================
    # LISTAR
    # ===============================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerPago()
            result = serialize_object(result)
            return [self._normalize(p) for p in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar pagos: {e}")

    # ===============================================================
    # OBTENER POR ID
    # ===============================================================
    def obtener_por_id(self, id_pago):
        try:
            result = self.client.service.ObtenerPagoPorId(id_pago)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener pago {id_pago}: {e}")

    # ===============================================================
    # CREAR
    # ===============================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearPago(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear pago: {e}")

    # ===============================================================
    # ACTUALIZAR
    # ===============================================================
    def actualizar(self, id_pago, dto):
        try:
            result = self.client.service.ActualizarPago(id_pago, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar pago {id_pago}: {e}")

    # ===============================================================
    # ELIMINAR (lógico)
    # ===============================================================
    def eliminar(self, id_pago):
        try:
            return self.client.service.EliminarPago(id_pago)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar pago {id_pago}: {e}")

    # ===============================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # ===============================================================
    def obtener_pagos(self):
        """Alias para listar()"""
        return self.listar()
    
    def obtener_pago_por_id(self, id_pago):
        """Alias para obtener_por_id()"""
        return self.obtener_por_id(id_pago)
    
    def crear_pago(self, id_metodo, id_usuario_ext, id_usuario, id_factura, cuenta_origen, cuenta_destino, monto, estado=True):
        dto = {
            "IdMetodoPago": id_metodo,
            "IdUnicoUsuarioExterno": id_usuario_ext,
            "IdUnicoUsuario": id_usuario,
            "IdFactura": id_factura,
            "CuentaOrigenPago": cuenta_origen,
            "CuentaDestinoPago": cuenta_destino,
            "MontoTotalPago": monto,
            "FechaEmisionPago": datetime.now().isoformat(),
            "EstadoPago": estado,
            "FechaModificacionPago": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_pago(self, id_pago, id_metodo, id_usuario_ext, id_usuario, id_factura, cuenta_origen, cuenta_destino, monto, estado=True):
        dto = {
            "IdPago": id_pago,
            "IdMetodoPago": id_metodo,
            "IdUnicoUsuarioExterno": id_usuario_ext,
            "IdUnicoUsuario": id_usuario,
            "IdFactura": id_factura,
            "CuentaOrigenPago": cuenta_origen,
            "CuentaDestinoPago": cuenta_destino,
            "MontoTotalPago": monto,
            "EstadoPago": estado,
            "FechaModificacionPago": datetime.now().isoformat()
        }
        return self.actualizar(id_pago, dto)
    
    def eliminar_pago(self, id_pago):
        """Alias para eliminar()"""
        return self.eliminar(id_pago)
