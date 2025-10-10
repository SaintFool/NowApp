# -----------------------------------------------------------------------------
# Dockerfile para la base de datos transaccional de NowApp
# -----------------------------------------------------------------------------
FROM postgres:16.10

ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=una_contraseña_muy_fuerte_123
ENV POSTGRES_DB=BD_Transaccional_NowApp

COPY ./init/ /docker-entrypoint-initdb.d/
