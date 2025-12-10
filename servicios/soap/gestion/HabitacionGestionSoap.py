import requests
from datetime import datetime
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class HabitacionGestionSoap:

    def __init__(self):
        # 🔥 WSDL de Habitaciones publicado en Azure
        self.wsdl = (
            "http://brisamargs.runasp.net/HabitacionWS.asmx?wsdl"
        )

        # Azure → SSL intermedio → permitir verify=False
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        transport = Transport(session=session)
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # =============================================================
    # NORMALIZAR → MISMO FORMATO QUE REST
    # =============================================================
    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        def fmt(dt):
            return dt.isoformat() if dt else None

        return {
            "IdHabitacion": d.get("IdHabitacion"),
            "IdTipoHabitacion": d.get("IdTipoHabitacion"),
            "IdCiudad": d.get("IdCiudad"),
            "IdHotel": d.get("IdHotel"),
            "NombreHabitacion": d.get("NombreHabitacion"),
            "NombreHotel": d.get("NombreHotel"),
            "NombreCiudad": d.get("NombreCiudad"),
            "PrecioNormalHabitacion": d.get("PrecioNormalHabitacion"),
            "PrecioActualHabitacion": d.get("PrecioActualHabitacion"),
            "CapacidadHabitacion": d.get("CapacidadHabitacion"),
            "EstadoHabitacion": d.get("EstadoHabitacion"),
            "FechaRegistroHabitacion": fmt(d.get("FechaRegistroHabitacion")),
            "EstadoActivoHabitacion": d.get("EstadoActivoHabitacion"),
            "FechaModificacionHabitacion": fmt(d.get("FechaModificacionHabitacion")),
        }

    # =============================================================
    # LISTAR
    # =============================================================
    def listar(self):
        try:
            result = self.client.service.ObtenerHabitaciones()
            result = serialize_object(result)
            return [self._normalize(x) for x in result]
        except Fault as e:
            raise Exception(f"Error SOAP al listar habitaciones: {e}")
    
    # Método alias para compatibilidad con REST
    def obtener_habitaciones(self):
        return self.listar()

    # =============================================================
    # OBTENER POR ID
    # =============================================================
    def obtener_por_id(self, id_hab):
        try:
            result = self.client.service.ObtenerHabitacionPorId(id_hab)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al obtener habitación ({id_hab}): {e}")

    # =============================================================
    # CREAR
    # =============================================================
    def crear(self, dto):
        try:
            result = self.client.service.CrearHabitacion(dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al crear habitación: {e}")

    # =============================================================
    # ACTUALIZAR
    # =============================================================
    def actualizar(self, id_hab, dto):
        try:
            result = self.client.service.ActualizarHabitacion(id_hab, dto)
            return self._normalize(result)
        except Fault as e:
            raise Exception(f"Error SOAP al actualizar habitación ({id_hab}): {e}")

    # =============================================================
    # ELIMINAR (lógica)
    # =============================================================
    def eliminar(self, id_hab):
        try:
            return self.client.service.EliminarHabitacion(id_hab)
        except Fault as e:
            raise Exception(f"Error SOAP al eliminar habitación ({id_hab}): {e}")

    # =============================================================
    # ALIAS PARA COMPATIBILIDAD CON VIEWS DEL ADMIN
    # =============================================================
    def crear_habitacion(self, id_habitacion, id_tipo, id_ciudad, id_hotel, nombre, precio_normal, precio_actual, capacidad, estado, estado_activo=True):
        """Alias para crear() - convierte parámetros a DTO"""
        dto = {
            "IdHabitacion": id_habitacion,
            "IdTipoHabitacion": id_tipo,
            "IdCiudad": id_ciudad,
            "IdHotel": id_hotel,
            "NombreHabitacion": nombre,
            "PrecioNormalHabitacion": precio_normal,
            "PrecioActualHabitacion": precio_actual,
            "CapacidadHabitacion": capacidad,
            "EstadoHabitacion": estado,
            "EstadoActivoHabitacion": estado_activo,
            "FechaModificacionHabitacion": datetime.now().isoformat()
        }
        return self.crear(dto)
    
    def actualizar_habitacion(self, id_habitacion, id_tipo, id_ciudad, id_hotel, nombre, precio_normal, precio_actual, capacidad, estado, estado_activo=True):
        """Alias para actualizar() - convierte parámetros a DTO"""
        dto = {
            "IdHabitacion": id_habitacion,
            "IdTipoHabitacion": id_tipo,
            "IdCiudad": id_ciudad,
            "IdHotel": id_hotel,
            "NombreHabitacion": nombre,
            "PrecioNormalHabitacion": precio_normal,
            "PrecioActualHabitacion": precio_actual,
            "CapacidadHabitacion": capacidad,
            "EstadoHabitacion": estado,
            "EstadoActivoHabitacion": estado_activo,
            "FechaModificacionHabitacion": datetime.now().isoformat()
        }
        return self.actualizar(id_habitacion, dto)
    
    def eliminar_habitacion(self, id_habitacion):
        """Alias para eliminar()"""
        return self.eliminar(id_habitacion)
