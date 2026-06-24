"""Stockage et chargement de l'index RAG (chunks.json + bm25.pkl, sans vector DB)."""
import json
import os
import pickle

from rank_bm25 import BM25Okapi

DOSSIER_INDEX = "index"
CHEMIN_BM25 = os.path.join(DOSSIER_INDEX, "bm25.pkl")
CHEMIN_CHUNKS = os.path.join(DOSSIER_INDEX, "chunks.json")


def sauvegarder_index(chunks: list[dict], bm25: BM25Okapi) -> None:
    os.makedirs(DOSSIER_INDEX, exist_ok=True)

    chunks_avec_id = [{"id": i, **chunk} for i, chunk in enumerate(chunks)]
    with open(CHEMIN_CHUNKS, "w", encoding="utf-8") as f:
        json.dump(chunks_avec_id, f, ensure_ascii=False, indent=2)

    with open(CHEMIN_BM25, "wb") as f:
        pickle.dump(bm25, f)


def charger_index() -> tuple[list[dict], BM25Okapi]:
    if not os.path.exists(CHEMIN_BM25) or not os.path.exists(CHEMIN_CHUNKS):
        print("ERREUR : index introuvable. Lance d'abord : python build_index.py")
        raise SystemExit(1)

    with open(CHEMIN_CHUNKS, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(CHEMIN_BM25, "rb") as f:
        bm25 = pickle.load(f)

    if len(chunks) != bm25.corpus_size:
        print("ERREUR : l'index est incoherent (chunks.json et bm25.pkl ne correspondent pas).")
        print("Relance : python build_index.py")
        raise SystemExit(1)

    return chunks, bm25
