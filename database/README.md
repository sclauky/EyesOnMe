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

## Migrations (dbmate)
Fichiers dans `migrations/`, nommés `AAAAMMJJHHMMSS_nom.sql` (format natif dbmate, évite les conflits entre branches), chacun avec `-- migrate:up` et `-- migrate:down`. Elles tournent avec le rôle `eyesonme_owner` : c'est lui qui doit créer les tables, sinon `eyesonme_app` n'a pas les droits.

La base n'est joignable que depuis `eyesonme_net` : on migre **depuis le serveur** (`ssh server-perso`, puis `cd ~/EyesOnMe/database`) :
```
docker compose run --rm tools up      # appliquer
docker compose run --rm tools down    # annuler la dernière
docker compose run --rm tools status
```
`tools` est une image dbmate (profil `tools`, absente d'un `docker compose up` normal). Après un changement local, copier `migrations/` sur le serveur (`scp -r`).

## API (FastAPI, dossier `api/`)
Lecture seule, rôle `eyesonme_app`, requêtes paramétrées. Conteneur `eyesonme_api`, publié sur `127.0.0.1:8200` uniquement (Nginx de l'hôte devant).

| Route | Réponse |
|---|---|
| `GET /gestures` | gestes connus |
| `GET /actions` | actions disponibles et format de leurs paramètres |
| `GET /profiles/{name}/bindings` | réglages d'un profil (404 si inconnu) |
| `GET /health` | `{"status":"ok"}` |

Variable `CORS_ORIGINS` (dans `.env`) : origines autorisées, séparées par des virgules ; `*` est refusé au démarrage. Lancer / mettre à jour : `docker compose up -d --build api`. Tests : `cd api && pip install -r requirements-dev.txt && pytest`.
Exemple de bloc Nginx (à poser dans un **nouveau** fichier de site, sans toucher aux existants) : `location / { proxy_pass http://127.0.0.1:8200; }` sous le sous-domaine choisi pour l'API, avec Certbot.

## Ajouter une action (sans migration)
1. Déclarer l'action : `INSERT INTO action_type (code, label, description, params_schema) VALUES ('keyboard.press', 'Appuyer sur une touche', '...', '{"key": "string"}');`
2. Lier un geste : `INSERT INTO binding (profile_name, gesture_code, hand, trigger, action_code, params) VALUES ('default', 'peace_sign', 'any', 'on_end', 'keyboard.press', '{"key": "esc"}');`
3. Exécuter en rôle propriétaire : `docker exec -i eyesonme_db psql -U eyesonme_owner -d eyesonme` (ou, pour un changement qui doit être reproductible, une nouvelle migration `*_add_action.sql`).
4. Vérifier : `curl http://127.0.0.1:8200/actions` depuis le serveur. Le logiciel implémentera l'action dans son dictionnaire (ticket MAEL-110).
