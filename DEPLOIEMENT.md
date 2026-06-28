# Mise en ligne de la vitrine (Streamlit Community Cloud)

Guide des étapes à faire par Siddik. Le code est déjà prêt : index versionné,
protection par mot de passe intégrée, dépendances figées dans requirements.txt.

## 1. Protéger ta dépense (à faire EN PREMIER, indispensable)
Sur https://console.anthropic.com :
- Garde un **crédit prépayé** (5 USD suffisent pour une vitrine), **sans carte liée**
  en paiement automatique. Ainsi, au pire, la démo s'arrête quand le crédit est
  épuisé : ta facture ne peut pas exploser.
- Optionnel : définir une **limite de dépense mensuelle** (Usage limits).

## 2. Déployer sur Streamlit Community Cloud (gratuit)
1. Aller sur https://share.streamlit.io et se connecter **avec le compte GitHub**
   qui possède le repo `Asad1201/assistant-fiscal`.
2. Cliquer **« New app »** → choisir le repo `Asad1201/assistant-fiscal`,
   branche `main`, fichier principal `app.py`.
3. Avant de déployer, ouvrir **« Advanced settings » → Secrets** et coller :
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-...ta vraie clé..."
   APP_PASSWORD = "un-mot-de-passe-au-choix"
   ```
   (Ces secrets remplacent le `.env`, qui n'est pas envoyé sur GitHub.)
4. Cliquer **« Deploy »**. Au bout de 1 à 2 minutes, l'app est en ligne avec une
   URL publique (ex. `https://assistant-fiscal.streamlit.app`).

## 3. Utiliser la vitrine
- L'app demande d'abord le **mot de passe** (celui mis dans `APP_PASSWORD`).
- Tu donnes le lien + le mot de passe aux prospects que tu veux impressionner.
- Pour une démo **ouverte** (sans mot de passe, lien partageable largement),
  il suffit de retirer `APP_PASSWORD` des secrets et de redémarrer l'app.
  À ne faire que si tu surveilles ta dépense (étape 1).

## 4. Mettre à jour la vitrine plus tard
- Toute modification poussée sur `main` redéploie l'app automatiquement.
- Si tu ajoutes des documents (nouveau guide, nouvelle loi) : relancer en local
  `python build_index.py`, puis **committer l'index reconstruit** (`index/`) et
  pousser. C'est l'index versionné qui est servi en ligne (Streamlit Cloud n'a
  pas les PDF sources pour le reconstruire lui-même).
