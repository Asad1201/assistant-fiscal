# Assistant IA Fiscal (Cameroun)

Assistant qui répond à des questions fiscales (IGS, DSF, ACF, échéances) en s'appuyant sur la documentation officielle, avec citation des sources. Projet vitrine freelance IA et base du futur SaaS fiscal.

## Stack
- Python 3.12
- SDK Anthropic (Claude)
- RAG (à venir)

## Mise en route
1. Active l'environnement virtuel (Windows PowerShell) :
   `.\venv\Scripts\Activate.ps1`
2. Installe les dépendances :
   `pip install -r requirements.txt`
3. Renseigne ta clé API Anthropic dans le fichier `.env` (voir `.env.example`).
4. Lance le test :
   `python hello.py`

## Feuille de route
1. [x] Fondation : environnement + premier appel à Claude
2. [ ] Base documentaire (textes fiscaux)
3. [ ] RAG : recherche dans les docs + réponse sourcée
4. [ ] Interface web (chat)
5. [ ] Mise en ligne (vitrine)
