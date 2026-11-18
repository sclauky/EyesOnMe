#!/bin/sh
# Exécuté une seule fois, à la création du volume. Crée le rôle applicatif limité.
set -eu
psql -v ON_ERROR_STOP=1 -v app_pw="$EYESONME_APP_PASSWORD" \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
CREATE ROLE eyesonme_app LOGIN PASSWORD :'app_pw'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO eyesonme_app;
-- Tables/séquences créées plus tard par eyesonme_owner (dbmate) : DML seulement.
ALTER DEFAULT PRIVILEGES FOR ROLE eyesonme_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO eyesonme_app;
ALTER DEFAULT PRIVILEGES FOR ROLE eyesonme_owner IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO eyesonme_app;
SQL
