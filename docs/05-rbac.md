# Validation du RBAC — application A

## Configuration

- Rôles du client Keycloak `django-app` : `reader` et `manager`.
- Mapper dédié : rôles du client transmis dans la claim `app_roles`
  de l’ID token.
- ID token validé par Authlib avant lecture des rôles.
- Rôles reconnus par Django : `reader` et `manager`.
- Contrôles effectués côté serveur.
- Application B non concernée par ces règles.

## Matrice vérifiée manuellement avec Alice

| Rôle | Tableau de bord | Rapports | Gestion |
|---|---|---|---|
| `reader` | Autorisé | Autorisé | Refusé, HTTP 403 |
| `manager` | Autorisé | Autorisé | Autorisé |
| Aucun | Autorisé | Refusé, HTTP 403 | Refusé, HTTP 403 |

Un nouveau parcours OIDC a été effectué après chaque modification
des rôles dans Keycloak. Les résultats navigateur ont été confirmés
par l’utilisateur.

## Tests automatisés

Commande depuis la racine du laboratoire, avec l’environnement virtuel actif :

```bash
python app/manage.py test iam_portal
```

Quatre tests réussis lors de l’implémentation :

- Matrice d’accès `reader`, `manager` et sans rôle autorisé.
- Refus lorsque les rôles sont absents ou mal formés.
- Redirection vers la connexion pour un visiteur non authentifié.
- Impossible d’obtenir un rôle via les paramètres de l’URL.

Ces tests vérifient les contrôles Django ; les tests manuels vérifient
également la transmission des rôles par Keycloak.

## Limite de révocation

Les rôles sont conservés dans la session Django après la connexion.
Une modification dans Keycloak ne met pas immédiatement à jour
une session existante.

L’expiration et la réévaluation des autorisations restent à durcir.

## État final

Alice possède uniquement `reader` pour `django-app`.
Sa session a été actualisée par un nouveau parcours OIDC.
Aucun secret ni jeton n’est enregistré dans ce document.
