import logging
import psycopg2
from psycopg2 import OperationalError
from app.core.config import settings  # Asegúrate de que apunte a tu Settings real

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PostgresSingleton:
    """
    Singleton que mantiene una única conexión activa a PostgreSQL.
    Si la conexión se pierde, se restablece automáticamente.
    Incluye validación y limpieza de caracteres no UTF-8 en la configuración.
    """

    _instance = None
    _connection = None

    def __new__(cls):
        """
        Crea una única instancia del singleton si no existe.
        """
        if cls._instance is None:
            logger.info("[PostgresSingleton] Creando instancia única de conexión PostgreSQL")
            cls._instance = super(PostgresSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Inicializa la conexión a PostgreSQL si no existe o está cerrada.
        """
        if self._connection is None or self._is_connection_closed():
            self._connect()

    def _connect(self):
        """
        Establece una nueva conexión PostgreSQL usando parámetros del settings.
        Limpia caracteres no UTF-8 y agrega logs de diagnóstico.
        """
        try:
            logger.info("[PostgresSingleton] Estableciendo nueva conexión con PostgreSQL...")

            # Validar y limpiar configuración
            config_values = {
                "DB": settings.POSTGRES_DB,
                "USER": settings.POSTGRES_USER,
                "PASSWORD": settings.POSTGRES_PASSWORD,
                "HOST": settings.POSTGRES_HOST,
                "PORT": settings.POSTGRES_PORT,
            }

            for name, value in config_values.items():
                if not isinstance(value, str):
                    value = str(value) 
                try:
                    value.encode("utf-8")
                except UnicodeEncodeError:
                    logger.warning(f"[PostgresSingleton] Valor no UTF-8 detectado en {name}: {repr(value)}")
                config_values[name] = value.encode("utf-8", "ignore").decode("utf-8")

            # Intentar conexión con valores limpios
            self._connection = psycopg2.connect(
                dbname=config_values["DB"],
                user=config_values["USER"],
                password=config_values["PASSWORD"],
                host=config_values["HOST"],
                port=config_values["PORT"],
            )

            # Modo seguro: solo lectura + autocommit
            self._connection.set_session(readonly=True, autocommit=True)
            logger.info("[PostgresSingleton] Conexión a PostgreSQL establecida correctamente.")

        except OperationalError as e:
            logger.error("[PostgresSingleton] Fallo al conectar con la base de datos", exc_info=True)
            raise RuntimeError(f"Database connection failed: {e}")

        except UnicodeDecodeError as e:
            logger.error("[PostgresSingleton] Error de codificación UTF-8 en configuración", exc_info=True)
            raise RuntimeError(f"Invalid UTF-8 character in database settings: {e}")

    def _is_connection_closed(self) -> bool:
        """
        Verifica si la conexión actual está cerrada.
        psycopg2 retorna 0 si está abierta, >0 si está cerrada.
        """
        try:
            return self._connection is None or self._connection.closed != 0
        except Exception:
            return True

    def get_connection(self):
        """
        Devuelve una conexión activa. Reconecta automáticamente si está cerrada.
        """
        if self._is_connection_closed():
            logger.warning("[PostgresSingleton] Conexión cerrada. Reintentando conexión...")
            self._connect()
        return self._connection


def get_postgres_instance():
    """
    Devuelve una conexión activa PostgreSQL desde el singleton.
    """
    return PostgresSingleton().get_connection()
