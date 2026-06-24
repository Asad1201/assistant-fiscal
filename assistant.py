"""Assistant fiscal avec RAG : repond a une question en s'appuyant sur les documents indexes.

Usage : python assistant.py "question"
"""
import argparse
import os
import sys

import anthropic
from dotenv import load_dotenv

from rag.recherche import rechercher
from rag.store import charger_index

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

SEUIL_PERTINENCE = 0.0

SYSTEM_PROMPT = """Tu es un assistant fiscal pour le Cameroun. Tu reponds UNIQUEMENT a partir des extraits de documents fournis ci-dessous, jamais a partir de connaissances generales.

Regles strictes :
1. Si les extraits fournis ne permettent pas de repondre a la question, dis-le explicitement ("Je ne trouve pas cette information dans les documents disponibles") plutot que de deviner ou de completer avec des connaissances generales.
2. Cite systematiquement ta source apres chaque affirmation, sous la forme (Source : <titre_document>, section "<section>").
3. Les dates limites et prorogations mentionnees dans les documents peuvent etre specifiques a une annee passee. Si la question porte sur une echeance actuelle et que les extraits ne mentionnent que des prorogations d'annees anterieures, precise clairement que ces dates ne sont pas forcement applicables a l'annee en cours plutot que de presumer une nouvelle prorogation.
4. Reponds en francais, de facon claire et concise."""


def construire_message(question: str, resultats: list[tuple[dict, float]]) -> str:
    extraits = []
    for i, (chunk, score) in enumerate(resultats):
        if chunk.get("section"):
            reference = f'section "{chunk["section"]}"'
        else:
            reference = f"page {chunk.get('page')}"
        extraits.append(f"[Extrait {i + 1} - {chunk['titre_document']}, {reference}]\n{chunk['texte']}")

    if not resultats or resultats[0][1] <= SEUIL_PERTINENCE:
        extraits.append("[Aucun extrait suffisamment pertinent n'a ete trouve]")

    contexte = "\n\n---\n\n".join(extraits)
    return f"Voici des extraits de documents fiscaux camerounais :\n\n{contexte}\n\n---\n\nQuestion : {question}"


def repondre(question: str, top_k: int = 8) -> str:
    chunks, bm25 = charger_index()
    resultats = rechercher(question, chunks, bm25, top_k=top_k)

    message_utilisateur = construire_message(question, resultats)

    client = anthropic.Anthropic()
    reponse = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message_utilisateur}],
    )

    return "".join(bloc.text for bloc in reponse.content if bloc.type == "text")


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

    print(repondre(args.question, top_k=args.top_k))


if __name__ == "__main__":
    main()
