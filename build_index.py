"""Construit l'index RAG a partir des documents (guides markdown + CGI PDF).

Usage : python build_index.py
"""
import glob
import os
import sys

from dotenv import load_dotenv

from ingestion.chunking import decouper_markdown
from ingestion.pdf import decouper_cgi, decouper_pdf_par_blocs
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

# Loi de finances 2026 : droit fiscal en vigueur, prime sur le CGI 2024 quand
# un meme article figure dans les deux (voir la regle du prompt systeme).
LF2026_PDF = "documents/lois-finances/LF_2026_texte_complet.pdf"
LF2026_TITRE = "Loi de finances 2026"
LF2026_URL = "https://www.dgb.cm/wp-content/uploads/2025/11/PROJET-DE-LOI-FINANCES-2026_FR_26112025.pdf"

LF2026_MESURES_PDF = "documents/lois-finances/LF_2026_mesures_fiscales_nouvelles.pdf"
LF2026_MESURES_TITRE = "Loi de finances 2026 - Mesures fiscales nouvelles"
LF2026_MESURES_URL = "https://bstp-cameroun.cm/assets/files/articlefile/125-0.pdf"


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

    # 3. Loi de finances 2026 (texte legal en vigueur, decoupe par article)
    if os.path.exists(LF2026_PDF):
        chunks_lf = decouper_cgi(LF2026_PDF, LF2026_TITRE, LF2026_URL, type_source="loi-finances-2026")
        chunks.extend(chunks_lf)
        print(f"{len(chunks_lf)} chunks (articles) extraits de la loi de finances 2026.")
    else:
        print(f"ATTENTION : {LF2026_PDF} introuvable, la LF 2026 n'est pas indexee.")

    # 4. Loi de finances 2026 - mesures fiscales nouvelles (synthese, par blocs)
    if os.path.exists(LF2026_MESURES_PDF):
        chunks_mes = decouper_pdf_par_blocs(LF2026_MESURES_PDF, LF2026_MESURES_TITRE, LF2026_MESURES_URL, type_source="loi-finances-2026")
        chunks.extend(chunks_mes)
        print(f"{len(chunks_mes)} chunks extraits des mesures fiscales nouvelles 2026.")
    else:
        print(f"ATTENTION : {LF2026_MESURES_PDF} introuvable, les mesures 2026 ne sont pas indexees.")

    bm25 = construire_bm25(chunks)

    sauvegarder_index(chunks, bm25)
    print(f"Index sauvegarde dans index/ ({len(chunks)} chunks au total).")


if __name__ == "__main__":
    main()
