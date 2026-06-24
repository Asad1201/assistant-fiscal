"""Logique de generation de la reponse (RAG + appel au modele), partagee
entre le CLI (assistant.py) et l'interface web (app.py).

On separe la recherche, la construction du message et l'appel au modele pour
que l'interface web puisse charger l'index une seule fois (cache) et streamer
la reponse au fur et a mesure.
"""
from rag.recherche import rechercher

MODELE = "claude-haiku-4-5"
MAX_TOKENS = 600
SEUIL_PERTINENCE = 0.0

SYSTEM_PROMPT = """Tu es un assistant fiscal pour le Cameroun. Tu reponds UNIQUEMENT a partir des extraits de documents fournis ci-dessous, jamais a partir de connaissances generales.

Regles strictes :
1. Si les extraits fournis ne permettent pas de repondre a la question, dis-le explicitement ("Je ne trouve pas cette information dans les documents disponibles") plutot que de deviner ou de completer avec des connaissances generales.
2. Cite systematiquement ta source apres chaque affirmation, sous la forme (Source : <titre_document>, section "<section>").
3. Les dates limites et prorogations mentionnees dans les documents peuvent etre specifiques a une annee passee. Si la question porte sur une echeance actuelle et que les extraits ne mentionnent que des prorogations d'annees anterieures, precise clairement que ces dates ne sont pas forcement applicables a l'annee en cours plutot que de presumer une nouvelle prorogation.
4. Reponds en francais, de facon claire et concise."""


def _reference(chunk: dict) -> str:
    if chunk.get("section"):
        return f'section "{chunk["section"]}"'
    return f"page {chunk.get('page')}"


def construire_message(question: str, resultats: list[tuple[dict, float]]) -> str:
    extraits = []
    for i, (chunk, _score) in enumerate(resultats):
        extraits.append(f"[Extrait {i + 1} - {chunk['titre_document']}, {_reference(chunk)}]\n{chunk['texte']}")

    if not resultats or resultats[0][1] <= SEUIL_PERTINENCE:
        extraits.append("[Aucun extrait suffisamment pertinent n'a ete trouve]")

    contexte = "\n\n---\n\n".join(extraits)
    return f"Voici des extraits de documents fiscaux camerounais :\n\n{contexte}\n\n---\n\nQuestion : {question}"


def sources_citees(resultats: list[tuple[dict, float]]) -> list[str]:
    """Liste lisible et sans doublon des documents reellement consultes."""
    vues = []
    for chunk, score in resultats:
        if score <= SEUIL_PERTINENCE:
            continue
        label = f"{chunk['titre_document']} ({_reference(chunk)})"
        if label not in vues:
            vues.append(label)
    return vues


def repondre_stream(client, chunks, bm25, question, top_k=8):
    """Genere la reponse en streaming. Renvoie (generateur_de_texte, resultats)."""
    resultats = rechercher(question, chunks, bm25, top_k=top_k)
    message = construire_message(question, resultats)

    def generer():
        with client.messages.stream(
            model=MODELE,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": message}],
        ) as stream:
            yield from stream.text_stream

    return generer(), resultats


def repondre(client, chunks, bm25, question, top_k=8) -> str:
    """Version non-streamee (pour le CLI) : assemble le texte complet."""
    generateur, _resultats = repondre_stream(client, chunks, bm25, question, top_k=top_k)
    return "".join(generateur)
