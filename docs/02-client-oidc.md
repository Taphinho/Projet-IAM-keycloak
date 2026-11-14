# Client OIDC de l’application Django

## Configuration Keycloak
- Realm : enterprise-lab
- Client ID : django-app
- Type : OpenID Connect
- Authentification du client : activée
- Méthode d’authentification : Client Id and Secret
- Standard flow : activé
- Direct access grants : désactivé
- Implicit flow : désactivé
- Service accounts roles : désactivé
- Authorization Services : désactivé
- Méthode PKCE obligatoire : S256

## Adresses prévues
- Application : http://localhost:8001/
- Retour de connexion autorisé :
  http://localhost:8000/oidc/callback/
- Web origins : vide
- Retour après déconnexion : à configurer ultérieurement

## Gestion des secrets
Le secret du client restera dans la configuration locale du serveur.
Il ne doit apparaître ni dans Git, ni dans le navigateur, ni dans
les captures ou journaux partagés.

## État de validation
Configuration enregistrée dans Keycloak.
Application Django et route de retour non encore implémentées.
Connexion OIDC et protection PKCE non encore testées de bout en bout.
