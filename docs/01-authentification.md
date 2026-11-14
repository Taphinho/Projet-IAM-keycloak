# Vérification de l’authentification utilisateur

## Environnement
- Keycloak : 26.8.2
- Realm : enterprise-lab
- Utilisateur fictif : alice
- Test effectué dans une fenêtre privée.

## Procédure et résultats
1. Créer Alice dans enterprise-lab : réussi.
2. Définir un mot de passe temporaire : réussi.
3. Se connecter à la console de compte : réussi.
4. Vérifier le changement obligatoire du mot de passe : réussi.
5. Se déconnecter.
6. Essayer l’ancien mot de passe : connexion refusée.
7. Utiliser le nouveau mot de passe : connexion réussie,
   sans nouvelle demande de changement.

## Limites
- Test manuel.
- Aucun test d’intégration avec Django à ce stade.
- Accès HTTP local en mode développement.

Aucun mot de passe ni jeton n’est conservé dans ce document.
