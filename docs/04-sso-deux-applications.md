# Démonstration SSO entre deux applications

## Architecture

- Fournisseur d’identité : Keycloak, realm enterprise-lab.
- Application A : http://localhost:8001 — client django-app.
- Application B : http://localhost:8002 — client portal-b.
- Chaque application possède son secret de client, sa clé Django,
  sa base SQLite et ses noms de cookies.
- Parcours : Authorization Code avec PKCE S256.

## Test de connexion

Test manuel dans une nouvelle session de navigation privée :

1. Connexion à A : mot de passe d’Alice demandé.
2. Accueil de B : visiteur non connecté.
3. Connexion à B : réussie sans nouvelle saisie du mot de passe.

Résultat : chaque application ouvre sa propre session locale
en s’appuyant sur la même session centrale Keycloak.

## Test de déconnexion

1. A et B possèdent une session authentifiée.
2. Déconnexion depuis A : sessions Django A et Keycloak fermées.
3. Nouvelle requête au tableau de bord B : accès toujours autorisé.
4. Déconnexion depuis B : session locale B fermée.
5. Nouvelle connexion à B : mot de passe redemandé.

## Limites observées

- Aucun mécanisme de propagation de déconnexion vers B configuré.
- Une session locale B peut survivre à la fermeture de la session Keycloak.
- Le SSO ne garantit pas une déconnexion simultanée des applications.
- Tests manuels en HTTP local ; serveurs en mode développement.

Aucun secret, mot de passe, jeton ou code d’autorisation
n’est conservé dans ce document.
