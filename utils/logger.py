"""
Logger profesional para la aplicación DevSync AI.
Proporciona configuración flexible de logging con soporte para diferentes niveles,
formato personalizado y handlers configurables.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime

class DevSyncLogger:
    """
    Logger profesional para DevSync AI.
    
    Attributes:
        name (str): Nombre del logger
        level (int): Nivel de logging
        format_str (str): Formato del mensaje de log
        handlers (list): Lista de handlers configurados
    """

    def __init__(
        self,
        name: str = "devsync",
        level: int = logging.INFO,
        format_str: Optional[str] = None
    ):
        """
        Inicializa el logger con configuración personalizada.

        Args:
            name (str): Nombre del logger
            level (int): Nivel de logging (default: INFO)
            format_str (Optional[str]): Formato personalizado del mensaje
        """
        self.name = name
        self.level = level
        self.format_str = format_str or (
            "[%(asctime)s] [%(levelname)s] [%(name)s] "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )
        self.handlers = []
        
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Configura el logger con los handlers y formato especificados."""
        logger = logging.getLogger(self.name)
        
        # Evita handlers duplicados
        if logger.handlers:
            return
            
        logger.setLevel(self.level)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(self.format_str, datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(console_handler)
        self.handlers.append(console_handler)

    def add_file_handler(
        self,
        filename: str,
        level: Optional[int] = None,
        format_str: Optional[str] = None
    ) -> None:
        """
        Agrega un handler para escribir logs a archivo.

        Args:
            filename (str): Ruta del archivo de log
            level (Optional[int]): Nivel de logging para este handler
            format_str (Optional[str]): Formato personalizado para este handler
        """
        logger = logging.getLogger(self.name)
        
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(level or self.level)
        file_handler.setFormatter(
            logging.Formatter(
                format_str or self.format_str,
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(file_handler)
        self.handlers.append(file_handler)

    def get_logger(self) -> logging.Logger:
        """
        Obtiene el logger configurado.

        Returns:
            logging.Logger: Logger configurado
        """
        return logging.getLogger(self.name)

def setup_logger(
    name: str = "devsync",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Función helper para configurar rápidamente un logger.

    Args:
        name (str): Nombre del logger
        level (int): Nivel de logging
        log_file (Optional[str]): Ruta opcional para archivo de log

    Returns:
        logging.Logger: Logger configurado
    """
    logger = DevSyncLogger(name=name, level=level)
    
    if log_file:
        logger.add_file_handler(log_file)
        
    return logger.get_logger() 