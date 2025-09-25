FROM postgres:16-alpine

# Default database credentials for local demo usage
ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=postgres

# Seed schema and demo data
COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
