"""
Rate Limiter profesional para FastAPI y entornos serverless.
Implementa un sistema de rate limiting thread-safe con soporte para múltiples claves
y períodos de tiempo configurables.
"""

import time
import threading
from collections import defaultdict
from typing import Callable, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter configurable por clave (IP, user_id, etc).
    Permite N requests por periodo de tiempo (segundos).
    Thread-safe y optimizado para entornos serverless.
    
    Attributes:
        calls (int): Número máximo de llamadas permitidas por periodo
        period (int): Periodo de tiempo en segundos
        storage (Dict[str, List[float]]): Almacenamiento de timestamps por clave
        lock (threading.Lock): Lock para operaciones thread-safe
    """

    def __init__(self, calls: int, period: int):
        """
        Inicializa el rate limiter.

        Args:
            calls (int): Número máximo de llamadas permitidas por periodo
            period (int): Periodo de tiempo en segundos
        """
        if calls < 1:
            raise ValueError("calls debe ser mayor que 0")
        if period < 1:
            raise ValueError("period debe ser mayor que 0")
            
        self.calls = calls
        self.period = period
        self.storage: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
        logger.info(f"RateLimiter inicializado: {calls} llamadas por {period} segundos")

    def _clean_old_records(self, key: str, now: float) -> None:
        """
        Limpia registros antiguos para una clave específica.

        Args:
            key (str): Clave a limpiar
            now (float): Timestamp actual
        """
        cutoff = now - self.period
        self.storage[key] = [ts for ts in self.storage[key] if ts > cutoff]

    def is_allowed(self, key: str) -> bool:
        """
        Verifica si una clave puede hacer una nueva request.

        Args:
            key (str): Clave a verificar (ej: IP, user_id)

        Returns:
            bool: True si está permitido, False si excede el límite
        """
        now = time.time()
        
        with self.lock:
            self._clean_old_records(key, now)
            current_calls = len(self.storage[key])
            
            if current_calls < self.calls:
                self.storage[key].append(now)
                logger.debug(f"Request permitida para {key}. Llamadas actuales: {current_calls + 1}")
                return True
                
            logger.warning(f"Rate limit excedido para {key}. Llamadas actuales: {current_calls}")
            return False

    def get_remaining_calls(self, key: str) -> int:
        """
        Obtiene el número de llamadas restantes para una clave.

        Args:
            key (str): Clave a verificar

        Returns:
            int: Número de llamadas restantes
        """
        now = time.time()
        with self.lock:
            self._clean_old_records(key, now)
            return max(0, self.calls - len(self.storage[key]))

    def get_reset_time(self, key: str) -> Optional[float]:
        """
        Obtiene el tiempo hasta que se resetea el rate limit para una clave.

        Args:
            key (str): Clave a verificar

        Returns:
            Optional[float]: Tiempo en segundos hasta el reset, o None si no hay registros
        """
        with self.lock:
            if not self.storage[key]:
                return None
            oldest = min(self.storage[key])
            return max(0, oldest + self.period - time.time())

    def fastapi_dependency(self, key_func: Callable) -> Callable:
        """
        Genera una dependencia de FastAPI para rate limiting.

        Args:
            key_func (Callable): Función que recibe Request y devuelve la clave

        Returns:
            Callable: Dependencia de FastAPI
        """
        from fastapi import Request, HTTPException, status

        async def dependency(request: Request):
            key = key_func(request)
            if not self.is_allowed(key):
                reset_time = self.get_reset_time(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "reset_in": f"{reset_time:.1f}s" if reset_time else None,
                        "remaining_calls": self.get_remaining_calls(key)
                    }
                )
        return dependency