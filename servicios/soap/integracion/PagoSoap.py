import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from servicios.rest.integracion.BancoRest import BancoRest


class PagoSoap:
    """
    Cliente híbrido SOAP/REST para procesar pagos.
    
    IMPORTANTE: Esta clase combina SOAP para las operaciones principales
    del hotel y REST para la comunicación con el banco (BancoRest).
    
    El flujo de pago es:
    1. Crear registro de pago en sistema hotel (SOAP)
    2. Procesar transacción bancaria (REST - BancoRest)
    3. Actualizar estado del pago según resultado (SOAP)
    """

    def __init__(self, wsdl_pago=None):
        """
        Inicializa el cliente híbrido de pagos.
        
        Parámetros:
            wsdl_pago (str, optional): URL del WSDL para operaciones de pago SOAP.
                                      Si no se proporciona, solo funcionará el procesamiento bancario REST.
        """
        # Cliente REST para operaciones bancarias
        self.banco_rest = BancoRest()
        
        # Cliente SOAP para operaciones de pago del hotel (si se proporciona WSDL)
        self.soap_client = None
        if wsdl_pago:
            session = requests.Session()
            session.verify = False
            requests.packages.urllib3.disable_warnings()
            
            transport = Transport(session=session)
            self.soap_client = Client(wsdl=wsdl_pago, transport=transport)

    def _normalize(self, d):
        """Normaliza respuesta SOAP"""
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(date):
            return date.isoformat() if date else None

        return {
            "idPago": d.get("IdPago"),
            "idReserva": d.get("IdReserva"),
            "idMetodoPago": d.get("IdMetodoPago"),
            "monto": d.get("Monto"),
            "fechaPago": fmt(d.get("FechaPago")),
            "estadoPago": d.get("EstadoPago"),
            "numeroTransaccion": d.get("NumeroTransaccion"),
            "mensaje": d.get("Mensaje")
        }

    def procesar_pago_bancario(
        self,
        cuenta_origen,
        cuenta_destino,
        monto,
        descripcion=None
    ):
        """
        Procesa un pago a través del servicio bancario REST.
        
        Parámetros:
            cuenta_origen (str): Número de cuenta origen
            cuenta_destino (str): Número de cuenta destino
            monto (float): Monto a transferir
            descripcion (str, optional): Descripción de la transacción
            
        Retorna:
            Diccionario con el resultado de la transacción bancaria
        """
        try:
            return self.banco_rest.procesar_pago(
                cuenta_origen=cuenta_origen,
                cuenta_destino=cuenta_destino,
                monto=monto,
                descripcion=descripcion
            )
        except Exception as e:
            raise Exception(f"Error al procesar pago bancario: {e}")

    def crear_pago(self, id_reserva, id_metodo_pago, monto):
        """
        Crea un registro de pago en el sistema hotel (SOAP).
        
        Parámetros:
            id_reserva (int): ID de la reserva
            id_metodo_pago (int): ID del método de pago
            monto (float): Monto del pago
            
        Retorna:
            Diccionario con los datos del pago creado
        """
        if not self.soap_client:
            raise Exception("No se ha configurado el cliente SOAP para operaciones de pago.")
        
        if not id_reserva or id_reserva <= 0:
            raise ValueError("id_reserva debe ser mayor que 0.")
        if not id_metodo_pago or id_metodo_pago <= 0:
            raise ValueError("id_metodo_pago debe ser mayor que 0.")
        if not monto or monto <= 0:
            raise ValueError("monto debe ser mayor que 0.")

        try:
            dto = {
                "IdReserva": id_reserva,
                "IdMetodoPago": id_metodo_pago,
                "Monto": monto
            }
            
            r = self.soap_client.service.CrearPago(dto)
            return self._normalize(r)
            
        except Fault as e:
            raise Exception(f"SOAP Error al crear pago: {e}")

    def procesar_pago_completo(
        self,
        id_reserva,
        id_metodo_pago,
        monto,
        cuenta_origen,
        cuenta_destino,
        descripcion=None
    ):
        """
        Flujo completo de pago: crea registro en hotel y procesa transacción bancaria.
        
        Parámetros:
            id_reserva (int): ID de la reserva
            id_metodo_pago (int): ID del método de pago
            monto (float): Monto del pago
            cuenta_origen (str): Cuenta bancaria origen
            cuenta_destino (str): Cuenta bancaria destino
            descripcion (str, optional): Descripción del pago
            
        Retorna:
            Diccionario con ambos resultados: pago_hotel y transaccion_bancaria
        """
        resultado = {
            "pago_hotel": None,
            "transaccion_bancaria": None,
            "estado": "PENDIENTE",
            "mensaje": ""
        }
        
        try:
            # 1. Crear registro de pago en el hotel (SOAP)
            if self.soap_client:
                pago_hotel = self.crear_pago(id_reserva, id_metodo_pago, monto)
                resultado["pago_hotel"] = pago_hotel
            
            # 2. Procesar transacción bancaria (REST)
            transaccion = self.procesar_pago_bancario(
                cuenta_origen=cuenta_origen,
                cuenta_destino=cuenta_destino,
                monto=monto,
                descripcion=descripcion or f"Pago reserva #{id_reserva}"
            )
            resultado["transaccion_bancaria"] = transaccion
            
            # 3. Determinar estado final
            if transaccion and transaccion.get("estado") == "EXITOSO":
                resultado["estado"] = "COMPLETADO"
                resultado["mensaje"] = "Pago procesado exitosamente"
            else:
                resultado["estado"] = "FALLIDO"
                resultado["mensaje"] = transaccion.get("mensaje", "Error en transacción bancaria")
            
            return resultado
            
        except Exception as e:
            resultado["estado"] = "ERROR"
            resultado["mensaje"] = str(e)
            return resultado
