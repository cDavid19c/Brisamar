# banco_rest.py
import requests
from typing import Optional, Dict, Any, List


class BancoRest:
    """
    Cliente REST para el API del banco.
    Base URL: http://mibanca.runasp.net
    """
    
    BASE_URL = "http://mibanca.runasp.net"
    
    # Cuentas fijas del sistema
    CUENTA_CLIENTE = "1727115820"  # Cuenta que usan todos los clientes
    CUENTA_HOTEL = "1727115810"    # Cuenta donde se reciben los pagos
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    # ============================================================
    # GET → Obtener cliente por cédula
    # ============================================================
    def obtener_cliente(self, cedula: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un cliente por su cédula.
        También obtiene sus cuentas asociadas.
        """
        try:
            # Obtener cliente
            url_cliente = f"{self.BASE_URL}/api/clientes/{cedula}"
            resp_cliente = requests.get(url_cliente, headers=self.headers)
            resp_cliente.raise_for_status()
            cliente = resp_cliente.json()
            
            if not cliente:
                return None
            
            # Obtener cuentas del cliente
            url_cuentas = f"{self.BASE_URL}/api/Cuentas/cliente/{cedula}"
            resp_cuentas = requests.get(url_cuentas, headers=self.headers)
            resp_cuentas.raise_for_status()
            cuentas = resp_cuentas.json()
            
            cliente["Cuentas"] = cuentas or []
            return cliente
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener cliente: {e}")
    
    # ============================================================
    # GET → Obtener cuenta por ID
    # ============================================================
    def obtener_cuenta(self, cuenta_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una cuenta por su ID.
        """
        try:
            url = f"{self.BASE_URL}/api/cuentas/{cuenta_id}"
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al obtener cuenta: {e}")
    
    # ============================================================
    # POST → Crear transacción
    # ============================================================
    def crear_transaccion(
        self,
        cuenta_origen: int,
        cuenta_destino: int,
        monto: float
    ) -> Dict[str, Any]:
        """
        Crea una transacción entre dos cuentas.
        """
        url = f"{self.BASE_URL}/api/Transacciones"
        
        payload = {
            "cuenta_origen": cuenta_origen,
            "cuenta_destino": cuenta_destino,
            "monto": monto
        }
        
        try:
            resp = requests.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            
            # Intentar parsear como JSON
            resultado = None
            respuesta_texto = resp.text.strip()
            
            try:
                resultado = resp.json()
            except (ValueError, requests.exceptions.JSONDecodeError):
                # Si no es JSON, usar el texto como mensaje
                resultado = respuesta_texto
            
            # Verificar si la respuesta indica éxito
            respuesta_lower = respuesta_texto.lower()
            if "correctamente" in respuesta_lower or resp.status_code == 200:
                # Si resultado es un string, crear un dict con el mensaje
                if isinstance(resultado, str):
                    return {"ok": True, "mensaje": resultado}
                else:
                    # Si es un dict, extraer el mensaje
                    mensaje = resultado.get("mensaje", "Transacción realizada correctamente") if isinstance(resultado, dict) else "Transacción realizada correctamente"
                    return {"ok": True, "mensaje": mensaje}
            else:
                # Error en la transacción
                if isinstance(resultado, str):
                    return {"ok": False, "mensaje": resultado}
                else:
                    mensaje = resultado.get("mensaje", "Error en la transacción") if isinstance(resultado, dict) else "Error en la transacción"
                    return {"ok": False, "mensaje": mensaje}
                
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al crear transacción: {e}")
    
    # ============================================================
    # POST → Obtener cuenta válida con saldo suficiente
    # ============================================================
    def obtener_cuenta_valida(self, cedula: str, monto: float) -> Optional[int]:
        """
        Busca una cuenta del cliente que tenga saldo suficiente.
        Retorna el ID de la cuenta o None si no hay saldo suficiente.
        """
        try:
            cliente = self.obtener_cliente(cedula)
            if not cliente or not cliente.get("Cuentas"):
                return None
            
            for cuenta in cliente["Cuentas"]:
                saldo = cuenta.get("saldo", 0)
                if saldo >= monto:
                    return cuenta.get("cuenta_id")
            
            return None
            
        except Exception as e:
            raise ConnectionError(f"Error al obtener cuenta válida: {e}")
    
    # ============================================================
    # POST → Realizar pago (transacción desde cuenta cliente a hotel)
    # ============================================================
    def realizar_pago(
        self,
        cedula_cliente: str,
        monto: float
    ) -> Dict[str, Any]:
        """
        Realiza un pago desde la cuenta compartida del cliente hacia la cuenta del hotel.
        Usa la cuenta compartida del cliente (0707001320) que todos los clientes usan.
        Obtiene el cuenta_id correcto desde el cliente_id.
        """
        try:
            # Obtener el cliente para encontrar su cuenta_id
            cliente_origen = self.obtener_cliente(self.CUENTA_CLIENTE)
            if not cliente_origen or not cliente_origen.get("Cuentas"):
                return {"ok": False, "mensaje": "No se encontró la cuenta del cliente (origen)"}
            
            # Obtener la primera cuenta del cliente (o la que tenga saldo suficiente)
            cuenta_origen_obj = None
            for cuenta in cliente_origen["Cuentas"]:
                if float(cuenta.get("saldo", 0)) >= monto:
                    cuenta_origen_obj = cuenta
                    break
            
            if not cuenta_origen_obj:
                # Si no hay cuenta con saldo suficiente, usar la primera
                cuenta_origen_obj = cliente_origen["Cuentas"][0]
            
            cuenta_origen_id = cuenta_origen_obj.get("cuenta_id")
            if not cuenta_origen_id:
                return {"ok": False, "mensaje": "No se pudo obtener el cuenta_id del cliente"}
            
            # Obtener el cliente del hotel para encontrar su cuenta_id
            cliente_destino = self.obtener_cliente(self.CUENTA_HOTEL)
            if not cliente_destino or not cliente_destino.get("Cuentas"):
                return {"ok": False, "mensaje": "No se encontró la cuenta del hotel (destino)"}
            
            # Obtener la primera cuenta del hotel
            cuenta_destino_obj = cliente_destino["Cuentas"][0]
            cuenta_destino_id = cuenta_destino_obj.get("cuenta_id")
            if not cuenta_destino_id:
                return {"ok": False, "mensaje": "No se pudo obtener el cuenta_id del hotel"}
            
            # Verificar saldo
            saldo_cliente = float(cuenta_origen_obj.get("saldo", 0))
            if saldo_cliente < monto:
                return {"ok": False, "mensaje": f"Saldo insuficiente. Saldo disponible: ${saldo_cliente:.2f}"}
            
            print(f"[DEBUG BancoRest] Realizando transacción:")
            print(f"  - Cuenta origen (cliente): cuenta_id={cuenta_origen_id}, cliente_id={self.CUENTA_CLIENTE}, saldo={saldo_cliente}")
            print(f"  - Cuenta destino (hotel): cuenta_id={cuenta_destino_id}, cliente_id={self.CUENTA_HOTEL}")
            print(f"  - Monto: {monto}")
            
            # Realizar transacción usando los cuenta_id correctos
            resultado = self.crear_transaccion(
                cuenta_origen=cuenta_origen_id,
                cuenta_destino=cuenta_destino_id,
                monto=monto
            )
            
            return resultado
            
        except Exception as e:
            import traceback
            print(f"[ERROR BancoRest] Error al realizar pago: {e}")
            print(f"[ERROR BancoRest] Traceback: {traceback.format_exc()}")
            return {"ok": False, "mensaje": f"Error al realizar el pago: {str(e)}"}

