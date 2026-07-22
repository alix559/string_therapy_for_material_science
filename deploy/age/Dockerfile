# Apache AGE = PostgreSQL + graph extension (required by string_therapy).
# Do NOT use Railway's managed Postgres plugin — it has no AGE.
FROM apache/age:latest

ENV POSTGRES_USER=postgres \
    POSTGRES_DB=string_therapy

# Match local string-therapy-db: AGE must be in shared_preload_libraries.
CMD ["postgres", "-c", "shared_preload_libraries=age"]
