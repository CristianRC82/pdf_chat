import logging
import psycopg2
from psycopg2 import OperationalError
from app.core.config import settings  # Make sure this import points to your Settings class

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PostgresSingleton:
    """
    Singleton that maintains a single active connection to PostgreSQL.
    If the connection is lost, it automatically reestablishes it.
    """

    _instance = None
    _connection = None

    def __new__(cls):
        """
        Creates a single instance of the singleton if it does not exist.
        """
        if cls._instance is None:
            logger.info("[PostgresSingleton] Creating singleton instance for PostgreSQL")
            cls._instance = super(PostgresSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the PostgreSQL connection if it doesn't exist or is closed.
        """
        if self._connection is None or self._is_connection_closed():
            self._connect()

    def _connect(self):
        """
        Establishes a new PostgreSQL connection using settings parameters.
        """
        try:
            logger.info("[PostgresSingleton] Establishing new PostgreSQL connection...")
            self._connection = psycopg2.connect(
                dbname=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
            )

            # Set session as read-only and enable autocommit for safety
            self._connection.set_session(readonly=True, autocommit=True)
            logger.info("[PostgresSingleton] PostgreSQL connection established successfully.")

        except OperationalError as e:
            logger.error("[PostgresSingleton] Database connection failed", exc_info=True)
            raise RuntimeError(f"Database connection failed: {e}")

    def _is_connection_closed(self) -> bool:
        """
        Checks whether the current connection is closed.
        psycopg2 returns an integer: 0 means open, >0 means closed.
        """
        try:
            return self._connection is None or self._connection.closed != 0
        except Exception:
            return True

    def get_connection(self):
        """
        Returns an active connection. Reconnects automatically if closed.
        """
        if self._is_connection_closed():
            logger.warning("[PostgresSingleton] Connection is closed. Reconnecting...")
            self._connect()
        return self._connection


def get_postgres_instance():
    """
    Returns an active PostgreSQL connection from the singleton.
    """
    return PostgresSingleton().get_connection()
