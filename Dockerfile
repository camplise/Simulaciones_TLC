# Usamos una imagen base de Python ligera (versión 3.9 o 3.10 funcionan bien)
FROM python:3.10-slim

# Evita que Python escriba archivos .pyc y fuerza la salida por consola (bueno para logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para Matplotlib y Scipy
# (A veces las imágenes slim necesitan gcc o librerías gráficas básicas)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero el requirements.txt para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (app.py)
COPY . .

# Streamlit corre por defecto en el puerto 8501, lo exponemos
EXPOSE 8501

# Chequeo de salud para que RunCloud/Docker sepa si la app sigue viva
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de inicio: importante poner address 0.0.0.0 para que sea accesible desde fuera
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
