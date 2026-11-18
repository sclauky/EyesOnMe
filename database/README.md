# Base de données EyesOnMe

PostgreSQL 16 en conteneur, déployé sur `server-perso` (projet compose `eyesonme`, conteneur `eyesonme_db`, volume `eyesonme_pgdata`, réseau `eyesonme_net`).

- Aucun port publié : l'API rejoint la base via `eyesonme_net` (hôte `eyesonme_db`, port 5432).
- Deux rôles : `eyesonme_owner` (migrations dbmate) et `eyesonme_app` (DML seulement, utilisé par l'API).
- Secrets dans `.env` (non versionné), modèle dans `.env.example`.

## Déploiement
```
cd ~/EyesOnMe/database && cp .env.example .env   # puis éditer les mots de passe
docker compose up -d
```

## Sauvegardes
`scripts/backup.sh` : `pg_dump -Fc` chaque nuit (cron 03:00), rotation 7 jours dans `~/EyesOnMe/backups`. Restauration : voir `RESTORE.md`.

## Copie hors site (non implémentée en V0)
Décision du 18/11 : pas de copie hors site tant que la base ne contient que le seed.
Option future : `rclone` vers Cloudflare R2 (10 Go gratuits, compatible S3).
Il suffirait d'ajouter `rclone copy "$BACKUP_DIR" r2:eyesonme-backups` à la fin de `backup.sh`.
