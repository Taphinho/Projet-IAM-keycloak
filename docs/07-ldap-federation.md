# OpenLDAP, TLS et fédération

## Objets

- Racine : `dc=enterprise,dc=test`.
- Utilisateurs : `ou=people,dc=enterprise,dc=test`.
- Bob : `uid=bob,ou=people,dc=enterprise,dc=test`.
- Compte de lecture : `cn=keycloak,ou=services,dc=enterprise,dc=test`.

Les modèles publics contiennent des marqueurs, pas des mots de passe. Les données et `cn=config` sont persistants. La configuration TLS est appliquée hors ligne à chaque démarrage, y compris aux volumes déjà initialisés. Ne jamais lancer deux serveurs sur les mêmes volumes.

## TLS

`sh scripts/generate_ldap_tls.sh` crée une CA locale et un certificat de serveur avec SAN `ldap`, valable un an. Les clés sont privées et exclues de Git ; la clé de CA n’est pas montée dans le conteneur. LDAP écoute seulement en LDAPS sur 636, sans port publié. Le nom à utiliser est `ldap`, celui du certificat. Keycloak reçoit uniquement la CA publique via `KC_TRUSTSTORE_PATHS`. Ne jamais désactiver la vérification TLS pour faire réussir un test.

Sources : [truststore Keycloak](https://www.keycloak.org/server/keycloak-truststore), [configuration TLS OpenLDAP](https://www.openldap.org/doc/admin26/tls.html).

## Tests à exécuter après passage à TLS

```bash
docker compose exec ldap ldapwhoami -x -H ldaps://ldap:636 \
  -D 'uid=bob,ou=people,dc=enterprise,dc=test' -W
```

Bon mot de passe de Bob : DN reconnu ; mauvais mot de passe : code LDAP 49. Le client utilise `/tls/ca.crt` via `LDAPTLS_CACERT`. Aucun mot de passe dans les arguments.

Avec le compte de lecture, `ldapsearch` doit retrouver Bob et omettre `userPassword`. Le fichier `ldap/test-denied-write.ldif` doit être refusé avec le code 50. Copier ce fichier dans `/tmp` du conteneur puis l’utiliser avec `ldapmodify -f` et `-W`, toujours sur `ldaps://ldap:636`.

Une recette réutilisable est fournie : `sh scripts/test_ldap.sh`. Elle utilise les secrets locaux du conteneur sans les afficher et effectue les tests positifs et négatifs.

## Fédération

Après provisionnement : User federation → enterprise-openldap. Vérifier : URL `ldaps://ldap:636`, mode READ_ONLY, bind DN technique, users DN `ou=people,...`, username `uid`, UUID `entryUUID`, classe `inetOrgPerson`, import activé, inscriptions LDAP désactivées. Les mappers nom/prénom/email doivent correspondre à `sn`, `givenName`, `mail` ; vérifier les mappers générés par Keycloak lors de la création du fournisseur.

Exécuter Test connection, puis Test authentication. Rechercher Bob dans Users ou synchroniser les utilisateurs. Il doit être lié au fournisseur LDAP. Dans une nouvelle session privée, accéder à A et utiliser Bob avec `LDAP_BOB_PASSWORD`. Le mot de passe est vérifié dans LDAP, non copié dans Django. Bob sans rôle doit obtenir 403 sur `/reports/` et `/management/`.

Refaire un essai avec mauvais mot de passe. Vérifier aussi l’échec lorsque la CA n’est pas reconnue dans un environnement de test isolé, sans affaiblir le laboratoire actif.

## État des preuves

Avant TLS : lecture de Bob, protection de userPassword et refus d’écriture confirmés par l’utilisateur. Lors de la clôture : mots de passe Bob, LDAPS, ACL, refus de CA inconnue et fermeture du port clair testés dans une instance jetable isolée. La fédération avec Keycloak et Bob dans Django restent non validés.
