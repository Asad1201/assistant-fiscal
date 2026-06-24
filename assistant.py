"""Assistant fiscal avec RAG (ligne de commande).

Usage : python assistant.py "question"
La logique RAG est partagee avec l'interface web dans rag/generation.py.
"""
import argparse
import os
import sys

import anthropic
from dotenv import load_dotenv

from rag.generation import repondre
from rag.store import charger_index

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Assistant fiscal Cameroun (RAG)")
    parser.add_argument(
        "question",
        nargs="?",
        default="Quelle est la duree de validite de l'Attestation de Conformite Fiscale ?",
        help="Question fiscale a poser",
    )
    parser.add_argument("--top-k", type=int, default=8, help="Nombre d'extraits a recuperer")
    args = parser.parse_args()

    if not args.question.strip():
        print("ERREUR : la question est vide.")
        raise SystemExit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERREUR : aucune cle ANTHROPIC_API_KEY trouvee. Verifie ton .env.")
        raise SystemExit(1)

    chunks, bm25 = charger_index()
    client = anthropic.Anthropic()
    print(repondre(client, chunks, bm25, args.question, top_k=args.top_k))


if __name__ == "__main__":
    main()
