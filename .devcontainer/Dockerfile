FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /workspace

# Copiar archivos de configuración
COPY requirements.txt .
COPY .pre-commit-config.yaml .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar pre-commit
RUN pip install pre-commit && pre-commit install

# Configurar variables de entorno
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 