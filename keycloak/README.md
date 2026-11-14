# Configuration reproductible

`scripts/provision_keycloak.py` configure via l’API d’administration le realm,
les deux clients confidentiels, PKCE, les rôles, le mapper et la fédération LDAPS
en lecture seule. Les secrets sont chargés depuis `.env`, jamais exportés ici.

Le script conserve les utilisateurs et leurs facteurs OTP existants. Sur un
nouvel environnement, Alice reçoit `Configure OTP` comme action obligatoire.
Il ne supprime pas le compte de démarrage sans demande explicite.

Le realm et les clients portent des noms de laboratoire réservés. Ne pas
exécuter ce provisionnement sur un serveur partagé ou de production : certains
paramètres de ces objets sont actualisés. Les mots de passe des comptes existants
ne sont pas réinitialisés.
