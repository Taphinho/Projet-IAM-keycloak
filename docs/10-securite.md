# Modèle de menaces et décisions de sécurité

## Actifs et frontières

Secrets clients, mots de passe, clés de signature Keycloak, CA locale, graines OTP et sessions. Frontières : navigateur/applications ; applications/fournisseur OIDC ; Keycloak/PostgreSQL ; Keycloak/LDAP ; administrateur/hôte Docker. Un accès administrateur à Docker permet d’accéder aux secrets du laboratoire : Docker n’est pas une frontière contre un administrateur hôte.

## Menaces et contrôles

| Menace | Contrôle / limite |
|---|---|
| Vol de code OIDC | PKCE S256, client confidentiel, retours exacts |
| Retour injecté | state et nonce gérés par Authlib, ID token validé |
| Confusion d’identités | Couple issuer + subject, jamais liaison par email seul |
| Élévation de privilège | Refus par défaut, rôles depuis ID token validé, aucun compte staff créé |
| CSRF de déconnexion | POST et protection CSRF, suivi state du retour |
| Interception LDAP | LDAPS et CA vérifiée, compte de lecture, aucun port publié |
| Fuite dans Git | Secrets/bases/certificats exclus ; audit avant export |
| Droits périmés | Session Django de 15 minutes ; instantané de rôles, révocation non immédiate |
| Compromission de sauvegarde | Copies privées contenant des secrets, chiffrement requis hors hôte |

Le réseau interne n’est pas un chiffrement. L’accès HTTP de développement reste une limite locale explicite. La configuration LDAP ne permet pas la lecture de userPassword au compte de liaison et n’accorde aucun droit d’écriture à Keycloak. L’administrateur LDAP peut contourner les ACL de sa base.

## Avant toute production

HTTPS, reverse proxy et serveur WSGI/ASGI adaptés ; suppression des comptes bootstrap ; MFA administrateurs et procédure de récupération testée ; secrets hors variables inspectables Docker ; contrôle d’accès aux sauvegardes ; journalisation sans paramètres OIDC ; verrouillage des dépendances avec hashes, images par digest, mises à jour surveillées ; tests de charge ; réévaluation des droits ; propagation de déconnexion si requise. Ce laboratoire ne fournit ni haute disponibilité ni PAM.
