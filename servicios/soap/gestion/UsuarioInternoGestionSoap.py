import requests
from zeep import Client, Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault


class UsuarioInternoGestionSoap:

    def __init__(self):
        # Asegúrate de que esta URL coincida con donde desplegaste el .asmx
        self.wsdl = "http://brisamargs.runasp.net/UsuarioInternoWS.asmx?wsdl"

        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        transport = Transport(session=session)

        # Crear el cliente SOAP
        self.client = Client(wsdl=self.wsdl, transport=transport)

    # -------------------------------------------
    # Helpers
    # -------------------------------------------
    def _fmt_date(self, value):
        if value is None:
            return None
        # Si ya es string, devuélvelo
        if isinstance(value, str):
            return value
        # Cualquier cosa que tenga isoformat
        try:
            return value.isoformat()
        except Exception:
            # Último recurso: string
            return str(value)

    def _normalize(self, d):
        if d is None:
            return None

        d = serialize_object(d)

        # Si lo que llega NO es dict, no intentes normalizar, devuélvelo crudo
        if not isinstance(d, dict):
            return d

        return {
            "Id": d.get("Id"),
            "IdRol": d.get("IdRol"),
            "Nombre": d.get("Nombre"),
            "Apellido": d.get("Apellido"),
            "Correo": d.get("Correo"),
            "Clave": d.get("Clave"),
            "Estado": d.get("Estado"),
            "FechaNacimiento": self._fmt_date(d.get("FechaNacimiento")),
            "FechaModificacion": self._fmt_date(d.get("FechaModificacion")),
            "TipoDocumento": d.get("TipoDocumento"),
            "Documento": d.get("Documento"),
        }

    # -------------------------------------------
    # Listar
    # -------------------------------------------
    def listar(self):
        """
        Devuelve la lista de usuarios internos normalizados.
        Si falla el SOAP, devuelve [] y loguea el error en consola.
        """
        try:
            # DEBUG: ver operaciones disponibles del servicio
            try:
                ops = list(self.client.service._binding._operations.keys())
                print("DEBUG UsuarioInterno SOAP - operaciones disponibles:", ops)
            except Exception as debug_e:
                print("DEBUG UsuarioInterno SOAP - no se pudieron obtener operaciones:", repr(debug_e))

            # Llamada principal al método Listar
            r = self.client.service.Listar()

            # DEBUG: ver la respuesta cruda
            print("DEBUG UsuarioInterno SOAP - respuesta cruda Listar():", r)

            data = serialize_object(r)
            print("DEBUG UsuarioInterno SOAP - respuesta serializada:", data)

            # Normalizar a lista
            if data is None:
                raw_list = []
            elif isinstance(data, list):
                raw_list = data
            elif isinstance(data, dict):
                # Caso típico asmx:
                # {'UsuarioInternoDto': [ {...}, {...} ]}
                # o {'ListarResult': {'UsuarioInternoDto': [ ... ]}}
                if len(data) == 1:
                    inner = list(data.values())[0]
                    if isinstance(inner, list):
                        raw_list = inner
                    elif isinstance(inner, dict) and len(inner) == 1:
                        # Un nivel más de anidación
                        inner2 = list(inner.values())[0]
                        raw_list = inner2 if isinstance(inner2, list) else [inner2]
                    else:
                        raw_list = [inner]
                else:
                    raw_list = [data]
            else:
                raw_list = [data]

            usuarios = [self._normalize(x) for x in raw_list]
            print("DEBUG UsuarioInterno SOAP - usuarios normalizados:", usuarios)
            return usuarios

        except Fault as e:
            # Errores SOAP (faults de .NET, por ejemplo)
            print("SOAP Fault al listar usuarios internos:", e)
            # No re-lanzamos para que el admin no tire 500, solo mostramos vacío
            return []
        except Exception as e:
            # Cualquier otro error (método no existe, etc.)
            print("ERROR al listar usuarios internos:", repr(e))
            return []

    def obtener_usuarios_internos(self):
        return self.listar()

    def obtener_usuario_interno_por_id(self, id_usuario):
        return self.obtener_por_id(id_usuario)

    # -------------------------------------------
    # Obtener por ID
    # -------------------------------------------
    def obtener_por_id(self, id_usuario):
        try:
            r = self.client.service.ObtenerPorId(id_usuario)
            print("DEBUG UsuarioInterno SOAP - ObtenerPorId crudo:", r)
            return self._normalize(r)
        except Fault as e:
            print("SOAP Fault al obtener usuario por ID:", e)
            return None
        except Exception as e:
            print("Error al obtener usuario interno por ID:", repr(e))
            return None

    # -------------------------------------------
    # Crear
    # -------------------------------------------
    def crear(self, dto):
        try:
            r = self.client.service.Crear(dto)
            print("DEBUG UsuarioInterno SOAP - Crear crudo:", r)
            return self._normalize(r)
        except Fault as e:
            print("SOAP Fault al crear usuario interno:", e)
            return None
        except Exception as e:
            print("Error al crear usuario interno:", repr(e))
            return None

    # -------------------------------------------
    # Actualizar
    # -------------------------------------------
    def actualizar(self, dto):
        try:
            r = self.client.service.Actualizar(dto)
            print("DEBUG UsuarioInterno SOAP - Actualizar crudo:", r)
            return self._normalize(r)
        except Fault as e:
            print("SOAP Fault al actualizar usuario interno:", e)
            return None
        except Exception as e:
            print("Error al actualizar usuario interno:", repr(e))
            return None

    # -------------------------------------------
    # Eliminar
    # -------------------------------------------
    def eliminar(self, id_usuario):
        try:
            r = self.client.service.Eliminar(id_usuario)
            print("DEBUG UsuarioInterno SOAP - Eliminar crudo:", r)
            return r
        except Fault as e:
            print("SOAP Fault al eliminar usuario interno:", e)
            return False
        except Exception as e:
            print("Error al eliminar usuario interno:", repr(e))
            return False

    # -------------------------------------------
    # Login
    # -------------------------------------------
    def login(self, correo, clave):
        try:
            r = self.client.service.IniciarSesion(correo, clave)
            print("DEBUG UsuarioInterno SOAP - IniciarSesion crudo:", r)
            return self._normalize(r)
        except Fault as e:
            print("SOAP Fault en login de usuario interno:", e)
            return None
        except Exception as e:
            print("Error en login de usuario interno:", repr(e))
            return None
