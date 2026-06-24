# Assistant IA Fiscal (Cameroun)

Assistant qui répond à des questions fiscales (IS, IGS, DSF, ACF, échéances, procédures) en s'appuyant sur la documentation officielle (Code Général des Impôts 2024 + guides DGI), avec **citation systématique des sources** et refus de répondre hors de ces documents. Projet vitrine freelance IA et base du futur SaaS fiscal.

## Stack
- Python 3.12
- SDK Anthropic (Claude Haiku 4.5)
- RAG local : recherche BM25 (sans embeddings ni base externe), index `chunks.json` + `bm25.pkl`
- Interface web : Streamlit

## Mise en route
1. Active l'environnement virtuel (Windows PowerShell) :
   `.\venv\Scripts\Activate.ps1`
2. Installe les dépendances :
   `pip install -r requirements.txt`
3. Renseigne ta clé API Anthropic dans le fichier `.env` (voir `.env.example`).
4. Place le PDF du CGI dans `documents/cgi/CGI_2024.pdf` (non versionné), puis construis l'index :
   `python build_index.py`
5. Lance l'assistant :
   - En ligne de commande : `python assistant.py "Quel est le taux de l'impôt sur les sociétés ?"`
   - En interface web : `streamlit run app.py`

## Architecture
- `ingestion/` : découpe des documents en extraits (`chunking.py` pour les guides markdown, `pdf.py` pour le CGI découpé **par article de loi**).
- `rag/` : `recherche.py` (BM25), `store.py` (index local), `generation.py` (construction du prompt + appel au modèle, logique partagée CLI/web).
- `build_index.py` : construit l'index documentaire.
- `assistant.py` : interface ligne de commande.
- `app.py` : interface web de chat (Streamlit).

## Feuille de route
1. [x] Fondation : environnement + premier appel à Claude
2. [x] Base documentaire (CGI 2024 + guides DGI)
3. [x] RAG : recherche dans les docs + réponse sourcée
4. [x] Interface web (chat Streamlit)
5. [ ] Mise en ligne (vitrine)
