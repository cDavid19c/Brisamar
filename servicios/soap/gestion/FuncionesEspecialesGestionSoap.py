import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from datetime import datetime


class FuncionesEspecialesGestionSoap:

    def __init__(self):
        self.wsdl = (
            "http://allpahousenycgs.runasp.net/GestionFuncionesEspecialesWS.asmx?wsdl"
        )

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # -------------------------------------------
    # Normalización
    # -------------------------------------------
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "Id": d.get("Id"),
            "IdReserva": d.get("IdReserva"),
            "IdHold": d.get("IdHold"),
            "IdHabitacion": d.get("IdHabitacion"),
            "IdUnicoUsuario": d.get("IdUnicoUsuario"),
            "FechaInicio": fmt(d.get("FechaInicio")),
            "FechaFin": fmt(d.get("FechaFin")),
            "NumeroHuespedes": d.get("NumeroHuespedes"),
            "Nombre": d.get("Nombre"),
            "Apellido": d.get("Apellido"),
            "Correo": d.get("Correo"),
            "TipoDocumento": d.get("TipoDocumento"),
            "Documento": d.get("Documento"),
            "DuracionHoldSeg": d.get("DuracionHoldSeg"),
            "PrecioActual": d.get("PrecioActual"),
            "UrlFactura": d.get("UrlFactura"),
            "CuentaOrigen": d.get("CuentaOrigen"),
            "CuentaDestino": d.get("CuentaDestino"),
            "Mensaje": d.get("Mensaje"),
            "Estado": d.get("Estado"),
        }

    # -------------------------------------------
    # Utilería para convertir fechas
    # -------------------------------------------
    @staticmethod
    def _to_iso(dt):
        """Convierte string o datetime → ISO 8601"""
        if isinstance(dt, datetime):
            return dt.isoformat()
        if isinstance(dt, str):
            return dt
        return None

    # -------------------------------------------
    # Crear PRE-RESERVA
    # -------------------------------------------
    def crear_prereserva(
        self,
        id_habitacion,
        fecha_inicio,
        fecha_fin,
        numero_huespedes,
        nombre=None,
        apellido=None,
        correo=None,
        tipo_documento=None,
        documento=None,
        duracion_hold_seg=None,
        precio_actual=None,
        id_usuario=None
    ):
        try:
            # El método SOAP acepta parámetros individuales, NO un DTO
            # Firma: idHabitacion, fechaInicio, fechaFin, numeroHuespedes, duracionHoldSegundos, precioActual, idUsuario
            r = self.client.service.crearPreReservaHabitacion(
                idHabitacion=str(id_habitacion) if id_habitacion else "",
                fechaInicio=self._to_iso(fecha_inicio),
                fechaFin=self._to_iso(fecha_fin),
                numeroHuespedes=int(numero_huespedes) if numero_huespedes else 1,
                duracionHoldSegundos=int(duracion_hold_seg) if duracion_hold_seg else 180,
                precioActual=float(precio_actual) if precio_actual else 0.0,
                idUsuario=int(id_usuario) if id_usuario else 0
            )
            
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al crear pre-reserva: {e}")
        except Exception as e:
            raise Exception(f"Error al crear pre-reserva: {e}")

    # -------------------------------------------
    # Confirmar reserva de usuario interno
    # -------------------------------------------
    def confirmar_reserva_interna(
        self,
        id_habitacion,
        id_hold,
        id_unico_usuario,
        fecha_inicio,
        fecha_fin,
        numero_huespedes
    ):
        try:
            dto = {
                "IdHabitacion": id_habitacion,
                "IdHold": id_hold,
                "IdUnicoUsuario": id_unico_usuario,
                "FechaInicio": self._to_iso(fecha_inicio),
                "FechaFin": self._to_iso(fecha_fin),
                "NumeroHuespedes": numero_huespedes
            }
            r = self.client.service.ConfirmarReservaInterna(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al confirmar reserva interna: {e}")

    # -------------------------------------------
    # Emitir factura (usuario interno)
    # -------------------------------------------
    def emitir_factura_interna(
        self,
        id_reserva,
        correo=None,
        url_factura=None
    ):
        try:
            dto = {
                "IdReserva": id_reserva,
                "Correo": correo,
                "UrlFactura": url_factura,
                "CuentaOrigen": "194",
                "CuentaDestino": "196"
            }
            r = self.client.service.EmitirFacturaInterna(dto)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al emitir factura interna: {e}")

    # -------------------------------------------
    # Cancelar pre-reserva
    # -------------------------------------------
    def cancelar_prereserva(self, id_hold):
        try:
            if not id_hold:
                raise ValueError("id_hold es obligatorio.")
            r = self.client.service.CancelarPreReserva(id_hold)
            return self._normalize(r)
        except Fault as e:
            raise Exception(f"SOAP Error al cancelar pre-reserva: {e}")