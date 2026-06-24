"""Decoupage de documents en chunks pour l'indexation RAG."""
import re

TAILLE_MAX_SECTION = 1500


def decouper_markdown(chemin_fichier: str) -> list[dict]:
    """Decoupe un guide markdown en chunks par section ##.

    Le titre H1 et l'en-tete '> Source :' sont extraits comme metadonnees
    du document (titre_document, source_url), jamais comme chunk a part.
    Chaque section ## devient un chunk (titre de section + contenu),
    avec un repli par paragraphe si la section depasse TAILLE_MAX_SECTION.
    """
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        texte = f.read()

    lignes = texte.splitlines()

    titre_document = ""
    source_url = ""
    for ligne in lignes:
        if ligne.startswith("# ") and not titre_document:
            titre_document = ligne[2:].strip()
        match_source = re.match(r">\s*Source\s*:\s*(\S+)", ligne)
        if match_source:
            source_url = match_source.group(1)

    sections = re.split(r"(?m)^## ", texte)[1:]

    chunks = []
    for section in sections:
        lignes_section = section.splitlines()
        titre_section = lignes_section[0].strip()
        contenu = "\n".join(lignes_section[1:]).strip()
        texte_chunk = f"## {titre_section}\n{contenu}"

        if len(texte_chunk) <= TAILLE_MAX_SECTION:
            chunks.append(_creer_chunk(texte_chunk, chemin_fichier, titre_document, titre_section, source_url))
        else:
            for sous_bloc in _decouper_par_paragraphe(texte_chunk, TAILLE_MAX_SECTION):
                chunks.append(_creer_chunk(sous_bloc, chemin_fichier, titre_document, titre_section, source_url))

    return chunks


def _decouper_par_paragraphe(texte: str, taille_max: int) -> list[str]:
    """Repli : regroupe les paragraphes (separes par une ligne vide) en blocs <= taille_max."""
    paragraphes = texte.split("\n\n")
    blocs = []
    bloc_courant = ""
    for paragraphe in paragraphes:
        candidat = f"{bloc_courant}\n\n{paragraphe}" if bloc_courant else paragraphe
        if len(candidat) > taille_max and bloc_courant:
            blocs.append(bloc_courant)
            bloc_courant = paragraphe
        else:
            bloc_courant = candidat
    if bloc_courant:
        blocs.append(bloc_courant)
    return blocs


def _creer_chunk(texte: str, source_fichier: str, titre_document: str, section: str, source_url: str) -> dict:
    return {
        "texte": texte,
        "source_fichier": source_fichier,
        "type_source": "guide",
        "titre_document": titre_document,
        "section": section,
        "page": None,
        "source_url": source_url,
    }
