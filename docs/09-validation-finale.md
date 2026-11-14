# Bilan de clôture — 14 novembre 2026

La phase pédagogique pas à pas est clôturée à la demande de l’utilisateur.
La clôture ne transforme pas les tests non exécutés en résultats réussis.

## Confirmé au cours des séances

- Persistance PostgreSQL et séparation du compte applicatif.
- Authentification Alice, changement de mot de passe temporaire.
- OIDC Authorization Code avec PKCE, session Django et callbacks incomplets refusés.
- SSO entre deux clients et cookies distincts.
- Déconnexion locale et centrale ; session de B non automatiquement supprimée.
- RBAC reader/manager/sans rôle, avec nouveaux échanges après modifications.
- MFA TOTP : enrôlement et codes correct/incorrect.
- LDAP avant TLS : recherche de Bob et restrictions du compte technique.

## Contrôles exécutés lors de la préparation finale

- Dépendances Python cohérentes (`pip check`).
- Contrôles système Django A et B sans erreur.
- Aucune migration manquante.
- Quatre tests RBAC A, trois tests de protection B et deux tests de configuration
  de provisionnement : neuf tests automatisés réussis.
- Syntaxe shell et configurations Compose de base et optionnelle valides.
- Image OpenLDAP construite ; démarrage LDAPS dans un conteneur jetable isolé,
  avec secrets de test et sans volumes du laboratoire existant.
- Bob reconnu avec bon mot de passe ; mauvais mot de passe refusé (49).
- Recherche autorisée ; `userPassword` non divulgué ; écriture refusée (50).
- CA inconnue refusée ; port LDAP clair 389 indisponible.
- Certificat local vérifié avec OpenSSL.
- Les mêmes contrôles LDAPS et ACL réussissent après redémarrage.
- Image Django construite ; les quatre tests de A et les trois tests de B
  réussissent également à l’intérieur de cette image, sans réseau.

## Non validé de bout en bout

- Provisionnement REST sur un Keycloak neuf et fédération Keycloak–LDAPS.
- Authentification de Bob dans Django via Keycloak.
- Récupération MFA et test MFA + SSO combinés.
- Remplacement effectif du compte administrateur dans le laboratoire existant.
- Restauration complète depuis les sauvegardes ; tests de charge.
- Déploiement de production HTTPS et propagation globale de déconnexion.

Les scripts et procédures correspondants sont livrés. Les tests unitaires de
configuration vérifient des propriétés locales ; ils ne prouvent pas que les
appels REST ont été exécutés avec succès.

## Publication

Seules les sources sélectionnées sont exportées. `.env`, bases SQLite, secrets,
clés, certificats locaux, sauvegardes, environnement virtuel et dossiers internes
ne font pas partie de la livraison. Le paquet est contrôlé contre les secrets
locaux connus ; cet audit ne remplace pas une revue de sécurité exhaustive.
