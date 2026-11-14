# Validation de l’intégration Django–Keycloak

## Architecture

- Django : http://localhost:8001
- Keycloak : http://localhost:8080
- Realm : enterprise-lab
- Client OIDC confidentiel : django-app
- Parcours : Authorization Code avec PKCE S256
- Correspondance des comptes : couple issuer + subject

## Tests effectués

- Connexion d’Alice via Keycloak : réussie.
- Ouverture et maintien d’une session Django : réussis.
- Appel direct du callback sans demande initiale : refusé.
- Tableau de bord avec session : accessible.
- Tableau de bord sans session : redirection vers la connexion.
- Déconnexion locale Django : réussie.
- Reconnexion sans mot de passe avec session Keycloak valide : réussie.
- Connexions successives : une seule correspondance OIDC.
- Compte local : actif, non staff et non superutilisateur.
- Mot de passe local utilisable : aucun.

## Déconnexion Django et Keycloak

- Déconnexion déclenchée par formulaire POST avec protection CSRF.
- Session Django supprimée.
- Demande de déconnexion envoyée à Keycloak avec un ID token hint.
- Retour de déconnexion vérifié avec state.
- Après déconnexion : accueil Django non authentifié.
- Nouvelle connexion : mot de passe redemandé par Keycloak.
- Requête GET sur la vue de déconnexion : refusée (HTTP 405).
- Retour de déconnexion sans state : refusé (HTTP 400).

Les parcours dans le navigateur ont été vérifiés manuellement par
l’utilisateur. Le branchement des routes et les deux refus HTTP ci-dessus
ont également été contrôlés dans l’environnement Django.

## Limites actuelles

- HTTP local et serveurs en mode développement.
- Compte administrateur Keycloak temporaire encore utilisé.
- Déconnexion testée avec une application ; propagation aux autres
  applications non encore vérifiée.
- Aucun rôle applicatif contrôlé à ce stade.
- Aucun test de SSO entre deux applications à ce stade.
- Tests manuels ; contrôles négatifs des jetons à approfondir.

Aucun secret, mot de passe, jeton ou code d’autorisation n’est conservé
dans ce document.
