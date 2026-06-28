"""Ingestion du Code General des Impots (PDF) en chunks par article.

Le CGI est un texte de loi structure en articles ("Article 492.-").
Cet article est l'unite legale naturelle et exactement ce qu'un assistant
fiscal doit pouvoir citer. On decoupe donc le PDF par article plutot qu'en
blocs de taille fixe, en gardant le numero de page d'origine pour la source.
"""
import bisect
import re

from pypdf import PdfReader

# En-tete repete en haut de chaque page, a retirer du texte indexe.
ENTETE_COURANTE = re.compile(r"^Code G[ée]n[ée]ral des Imp[ôo]ts\b.*$")

# Un en-tete d'article : "Article 492.-", "Article 17 bis.-", "Article 1er.-",
# ou un article du Livre des Procedures Fiscales "Article L 94 bis.-".
# Le ".-" distingue le vrai en-tete d'une simple reference ("l'Article 476 ci-dessus").
ENTETE_ARTICLE = re.compile(r"Article\s+(L\s*)?(\d+(?:\s*(?:er|bis|ter|quater))?)\s*\.\s*-")

# Au-dela de cette taille, un article est resegmente en sous-blocs.
TAILLE_MAX_ARTICLE = 2500


def _nettoyer_page(texte: str) -> str:
    """Retire l'en-tete courante et les numeros de page, puis recolle les lignes.

    Le CGI est en colonnes etroites : le texte sort avec de nombreux sauts de
    ligne en milieu de phrase. On les remplace par des espaces pour reconstituer
    des phrases lisibles et indexables.
    """
    # pypdf produit parfois des "surrogates" isoles (U+D800..U+DFFF) non
    # encodables en UTF-8 : on les retire avant tout traitement.
    texte = texte.encode("utf-8", "ignore").decode("utf-8")

    lignes_propres = []
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        if ENTETE_COURANTE.match(ligne):
            continue
        if ligne.isdigit():  # numero de page imprime, isole sur sa ligne
            continue
        lignes_propres.append(ligne)
    texte = " ".join(lignes_propres)
    return re.sub(r"\s+", " ", texte).strip()


def decouper_cgi(chemin_pdf: str, titre_document: str, source_url: str, type_source: str = "cgi") -> list[dict]:
    """Decoupe un PDF de loi en chunks, un par article, avec page d'origine.

    Convient au CGI comme a la loi de finances : tout texte legal structure en
    "Article N.-". `type_source` distingue l'origine (cgi, loi-finances-2026...).
    """
    reader = PdfReader(chemin_pdf)

    # Concatene tout le document en suivant l'offset de debut de chaque page,
    # pour pouvoir retrouver la page d'un article a partir de sa position.
    texte_complet = ""
    debuts_de_page = []  # debuts_de_page[i] = offset du 1er caractere de la page i
    for page in reader.pages:
        debuts_de_page.append(len(texte_complet))
        texte_complet += _nettoyer_page(page.extract_text()) + " "

    def page_de(offset: int) -> int:
        # numero de page imprime ~ index 0-based de la page d'extraction
        return bisect.bisect_right(debuts_de_page, offset)

    entetes = list(ENTETE_ARTICLE.finditer(texte_complet))
    if not entetes:
        return []

    chunks = []
    for i, match in enumerate(entetes):
        debut = match.start()
        fin = entetes[i + 1].start() if i + 1 < len(entetes) else len(texte_complet)
        prefixe = match.group(1) or ""
        numero = re.sub(r"\s+", " ", prefixe + match.group(2)).strip()
        texte_article = texte_complet[debut:fin].strip()
        section = f"Article {numero}"
        page = page_de(debut)

        if len(texte_article) <= TAILLE_MAX_ARTICLE:
            chunks.append(_creer_chunk(texte_article, chemin_pdf, titre_document, section, page, source_url, type_source))
        else:
            for j, sous_bloc in enumerate(_resegmenter(texte_article, TAILLE_MAX_ARTICLE)):
                titre_sous = section if j == 0 else f"{section} (suite {j + 1})"
                chunks.append(_creer_chunk(sous_bloc, chemin_pdf, titre_document, titre_sous, page, source_url, type_source))

    return chunks


def decouper_pdf_par_blocs(chemin_pdf: str, titre_document: str, source_url: str,
                           type_source: str, taille_bloc: int = 1500) -> list[dict]:
    """Decoupe un PDF non structure en articles (note de synthese, circulaire)
    en blocs de taille bornee, page par page, avec le numero de page en source.

    Sert aux documents thematiques (ex : "mesures fiscales nouvelles") ou il n'y
    a pas d'"Article N.-" a isoler : on garde la granularite par page pour une
    citation fiable, et on resegmente les pages trop longues.
    """
    reader = PdfReader(chemin_pdf)
    chunks = []
    for index_page, page in enumerate(reader.pages):
        texte = _nettoyer_page(page.extract_text())
        if len(texte) < 40:  # page de garde / quasi vide : on ignore
            continue
        numero_page = index_page + 1
        section = f"page {numero_page}"
        if len(texte) <= taille_bloc:
            chunks.append(_creer_chunk(texte, chemin_pdf, titre_document, section, numero_page, source_url, type_source))
        else:
            for j, sous_bloc in enumerate(_resegmenter(texte, taille_bloc)):
                titre_sous = section if j == 0 else f"{section} (suite {j + 1})"
                chunks.append(_creer_chunk(sous_bloc, chemin_pdf, titre_document, titre_sous, numero_page, source_url, type_source))
    return chunks


def _resegmenter(texte: str, taille_max: int) -> list[str]:
    """Decoupe un long article en blocs <= taille_max sans couper un mot."""
    mots = texte.split(" ")
    blocs = []
    courant = ""
    for mot in mots:
        candidat = f"{courant} {mot}" if courant else mot
        if len(candidat) > taille_max and courant:
            blocs.append(courant)
            courant = mot
        else:
            courant = candidat
    if courant:
        blocs.append(courant)
    return blocs


def _creer_chunk(texte: str, source_fichier: str, titre_document: str, section: str, page: int, source_url: str, type_source: str = "cgi") -> dict:
    return {
        "texte": texte,
        "source_fichier": source_fichier,
        "type_source": type_source,
        "titre_document": titre_document,
        "section": section,
        "page": page,
        "source_url": source_url,
    }
