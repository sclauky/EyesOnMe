# Restauration de la base EyesOnMe

Dumps : `~/EyesOnMe/backups/eyesonme-AAAAMMJJ-HHMMSS.dump` (format custom `pg_dump -Fc`, nocturne à 03:00 via le timer systemd utilisateur `eyesonme-backup.timer`, 7 jours conservés).

## Tester une restauration (conteneur jetable, sans réseau)
```
cd ~/EyesOnMe
docker run -d --rm --name eyesonme_restore_test --network none -e POSTGRES_PASSWORD=x \
  -v "$PWD/backups:/b:ro" postgres:16.6-alpine
sleep 12
docker exec eyesonme_restore_test psql -U postgres -c "create role eyesonme_owner superuser; create role eyesonme_app;"
docker exec eyesonme_restore_test sh -c "createdb -U postgres eyesonme && pg_restore -U postgres -d eyesonme /b/<fichier>.dump"
docker exec eyesonme_restore_test psql -U postgres -d eyesonme -c "\dt" -c "select * from profile"
docker stop eyesonme_restore_test
```

## Restaurer pour de vrai (perte du volume)
1. `cd ~/EyesOnMe/database && docker compose down -v` (supprime le volume).
2. `docker compose up -d` : le script `initdb/01-roles.sh` recrée les rôles.
3. `docker exec -i eyesonme_db pg_restore -U eyesonme_owner -d eyesonme --no-owner < ../backups/<fichier>.dump`
4. Sans dump exploitable : rejouer `dbmate up` + le seed.

## Journal des tests
| Date | Dump | Résultat |
|---|---|---|
| 2026-11-18 | eyesonme-20261118-160024.dump | OK — restauré dans un conteneur jetable, table `profile` présente avec la ligne `default`. (Test fait avec une table de démonstration : le schéma réel arrive avec les migrations du ticket suivant ; à refaire une fois `dbmate up` + seed passés.) |
