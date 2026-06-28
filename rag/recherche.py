"""Recherche par mots-cles (BM25) dans les chunks indexes, sans embeddings."""
import re
import unicodedata

from rank_bm25 import BM25Okapi


def tokeniser(texte: str) -> list[str]:
    # Ignore les accents : une question tapee sans accents (frequent en saisie rapide)
    # doit pouvoir matcher les memes mots accentues dans les documents sources.
    texte_sans_accents = unicodedata.normalize("NFKD", texte.lower())
    texte_sans_accents = "".join(c for c in texte_sans_accents if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", texte_sans_accents)


def _texte_indexable(chunk: dict) -> str:
    """Texte sur lequel BM25 indexe un chunk : on prefixe le titre du document
    (et la section) au contenu. Sans ca, un petit chunk decoupe par section (ex.
    "Coût et validité") perd le sujet du document (ex. "ACF") present seulement
    dans le titre, et devient introuvable sur une question qui cite ce sujet.
    """
    titre = chunk.get("titre_document") or ""
    section = chunk.get("section") or ""
    return f"{titre} {section} {chunk['texte']}"


def construire_bm25(chunks: list[dict]) -> BM25Okapi:
    corpus_tokenise = [tokeniser(_texte_indexable(chunk)) for chunk in chunks]
    return BM25Okapi(corpus_tokenise)


def rechercher(question: str, chunks: list[dict], bm25: BM25Okapi, top_k: int = 4) -> list[tuple[dict, float]]:
    tokens_question = tokeniser(question)
    scores = bm25.get_scores(tokens_question)
    indices_tries = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]
    return [(chunks[i], float(scores[i])) for i in indices_tries]
