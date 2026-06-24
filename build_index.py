"""Construit l'index RAG a partir des documents (guides markdown + CGI PDF).

Usage : python build_index.py
"""
import glob
import os
import sys

from dotenv import load_dotenv

from ingestion.chunking import decouper_markdown
from ingestion.pdf import decouper_cgi
from rag.recherche import construire_bm25
from rag.store import sauvegarder_index

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

CGI_PDF = "documents/cgi/CGI_2024.pdf"
CGI_TITRE = "Code Général des Impôts 2024"
CGI_SOURCE_URL = "https://www.impots.cm/sites/default/files/documents/CGI%202024%20version%20francaise.pdf"


def main():
    chunks = []

    # 1. Guides pratiques (markdown)
    fichiers_guides = sorted(f.replace("\\", "/") for f in glob.glob("documents/guides/*.md"))
    if not fichiers_guides:
        print("ERREUR : aucun guide trouve dans documents/guides/")
        raise SystemExit(1)
    for fichier in fichiers_guides:
        chunks.extend(decouper_markdown(fichier))
    print(f"{len(chunks)} chunks extraits de {len(fichiers_guides)} guides.")

    # 2. Code General des Impots (PDF, decoupe par article)
    if os.path.exists(CGI_PDF):
        chunks_cgi = decouper_cgi(CGI_PDF, CGI_TITRE, CGI_SOURCE_URL)
        chunks.extend(chunks_cgi)
        print(f"{len(chunks_cgi)} chunks (articles) extraits du CGI.")
    else:
        print(f"ATTENTION : {CGI_PDF} introuvable, le CGI n'est pas indexe.")

    bm25 = construire_bm25(chunks)

    sauvegarder_index(chunks, bm25)
    print(f"Index sauvegarde dans index/ ({len(chunks)} chunks au total).")


if __name__ == "__main__":
    main()
