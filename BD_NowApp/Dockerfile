# -----------------------------------------------------------------------------
# Dockerfile para la base de datos transaccional de NowApp
# -----------------------------------------------------------------------------

# Paso 1: Usar la imagen oficial de PostgreSQL como base.
# Es una buena práctica usar una versión específica para asegurar que el entorno
# sea siempre el mismo. Usemos la versión 16.
FROM postgres:16.10

# Paso 2: Establecer las variables de entorno para la configuración inicial.
# PostgreSQL usará estas variables para crear un superusuario y una base de datos.
# ¡IMPORTANTE! En un proyecto real, nunca pongas contraseñas aquí.
# Se usan herramientas como "secrets" de Docker o variables de entorno del sistema.
# Para tu portafolio, esto está bien.
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=una_contraseña_muy_fuerte_123
ENV POSTGRES_DB=BD_Transaccional_NowApp

# Paso 3: Copiar nuestros scripts SQL al directorio de inicialización.
# Este es el paso clave. La imagen de PostgreSQL está diseñada para buscar
# y ejecutar automáticamente cualquier script .sql o .sh que encuentre aquí
# la PRIMERA VEZ que se inicie el contenedor.
COPY ./init/ /docker-entrypoint-initdb.d/
