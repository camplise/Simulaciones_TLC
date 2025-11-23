# Usamos una imagen base de Python ligera
FROM python:3.10-slim

# Evita que Python escriba archivos .pyc y fuerza la salida por consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# IMPORTANTE: Configura Matplotlib para trabajar sin pantalla
ENV MPLBACKEND=Agg

# Directorio de trabajo
WORKDIR /app

# --- AQUÍ ESTÁ EL CAMBIO CRÍTICO ---
# Hemos eliminado 'software-properties-common'.
# Solo instalamos 'build-essential' y 'curl'.
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
# -----------------------------------

# Copiamos primero el requirements.txt
COPY requirements.txt .

# Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto
EXPOSE 8501

# Chequeo de salud
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de inicio
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
