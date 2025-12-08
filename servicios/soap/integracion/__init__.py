# Servicios SOAP de Integración
# Estos servicios se conectan con las APIs externas del hotel

from .HabitacionesSoap import HabitacionesSoap
from .DisponibilidadSoap import DisponibilidadSoap
from .PreReservaSoap import PreReservaSoap
from .ConfirmarReservaSoap import ConfirmarReservaSoap
from .UsuarioExternoSoap import UsuarioExternoSoap
from .FacturaSoap import FacturaSoap
from .ReservaSoap import ReservaSoap
from .PagoSoap import PagoSoap

__all__ = [
    'HabitacionesSoap',
    'DisponibilidadSoap',
    'PreReservaSoap',
    'ConfirmarReservaSoap',
    'UsuarioExternoSoap',
    'FacturaSoap',
    'ReservaSoap',
    'PagoSoap'
]
