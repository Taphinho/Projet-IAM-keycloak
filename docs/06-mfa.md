# MFA TOTP

## Preuves manuelles confirmées

Alice a été enrôlée avec l’action obligatoire `Configure OTP`. Une nouvelle session privée a exigé le mot de passe puis un code TOTP. Un code incorrect a été refusé ; un code valide a permis l’accès. Aucun secret d’enrôlement, QR code ni code OTP n’est enregistré dans le dépôt.

## Ce qui reste à vérifier

La récupération a été volontairement interrompue à la demande de l’utilisateur. Si `Configure OTP` a été remis en attente pendant cette préparation, vérifier sa présence et terminer ou retirer l’action avant de reprendre un test ordinaire. Le test combinant MFA et SSO n’a pas été confirmé.

## Récupération assistée à tester

Vérifier l’identité du demandeur par une procédure indépendante ; enregistrer un ticket ; imposer `Configure OTP` ; révoquer ses sessions ; supprimer seulement l’ancien authentificateur ; faire enrôler un nouveau dispositif ; vérifier qu’un mot de passe seul ne permet pas d’accéder au compte. Documenter l’opérateur et le résultat sans capturer les secrets. Ne pas supprimer les facteurs pour contourner un incident sans vérification d’identité.

Sur le flux Browser par défaut, OTP est conditionnel à la configuration du compte. L’enrôlement d’Alice ne constitue donc pas une obligation MFA universelle du realm. Pour généraliser cette obligation, dupliquer le flux, configurer les exigences et tester d’abord sur un realm isolé. TOTP n’est pas résistant au phishing ; WebAuthn est une extension future.
