"""Interface web de l'assistant fiscal (Streamlit).

Lancement : streamlit run app.py
Reutilise la logique RAG de rag/generation.py (la meme que le CLI assistant.py).
"""
import os

import anthropic
import streamlit as st
from dotenv import load_dotenv

from rag.generation import repondre_stream, sources_citees
from rag.store import CHEMIN_CHUNKS, charger_index

load_dotenv()

st.set_page_config(page_title="Assistant Fiscal Cameroun", page_icon="📑", layout="centered")


@st.cache_resource(show_spinner="Chargement de l'index documentaire...")
def _charger_index():
    return charger_index()


@st.cache_resource
def _client():
    return anthropic.Anthropic()


MESSAGE_ACCUEIL = (
    "Bonjour. Je suis un assistant fiscal pour le Cameroun. Je reponds a partir du "
    "Code General des Impots et de guides pratiques (DSF, ACF, immatriculation, Harmony 2), "
    "en citant mes sources. Pose-moi une question."
)

EXEMPLES = [
    "Quel est le taux de l'impot sur les societes ?",
    "Quelle est la duree de validite de l'ACF ?",
    "Quelles sont les dates limites de la DSF ?",
]

# --- Verifications de demarrage ---
st.title("📑 Assistant Fiscal Cameroun")
st.caption("RAG sur le Code General des Impots + guides pratiques. Reponses sourcees, sans invention.")

if not os.environ.get("ANTHROPIC_API_KEY"):
    st.error("Aucune cle ANTHROPIC_API_KEY trouvee. Renseigne-la dans le fichier .env.")
    st.stop()

if not os.path.exists(CHEMIN_CHUNKS):
    st.error("Index introuvable. Lance d'abord dans un terminal : python build_index.py")
    st.stop()

chunks, bm25 = _charger_index()

# --- Barre laterale ---
with st.sidebar:
    st.header("A propos")
    st.markdown(
        f"- **{len(chunks)} extraits** indexes\n"
        "- Sources : Code General des Impots 2024 + guides DGI\n"
        "- L'assistant **cite ses sources** et refuse de repondre hors de ces documents"
    )
    top_k = st.slider("Nombre d'extraits consultes", min_value=3, max_value=15, value=8)
    st.divider()
    st.caption("Prototype vitrine. Ne remplace pas un conseil fiscal personnalise.")

# --- Historique de conversation ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": MESSAGE_ACCUEIL, "sources": []}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"Sources consultees ({len(message['sources'])})"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")


def _poser(question: str):
    st.session_state.messages.append({"role": "user", "content": question, "sources": []})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        generateur, resultats = repondre_stream(_client(), chunks, bm25, question, top_k=top_k)
        reponse = st.write_stream(generateur)
        sources = sources_citees(resultats)
        if sources:
            with st.expander(f"Sources consultees ({len(sources)})"):
                for source in sources:
                    st.markdown(f"- {source}")

    st.session_state.messages.append({"role": "assistant", "content": reponse, "sources": sources})


# --- Suggestions (seulement au premier ecran) ---
if len(st.session_state.messages) == 1:
    st.markdown("**Quelques exemples :**")
    cols = st.columns(len(EXEMPLES))
    for col, exemple in zip(cols, EXEMPLES):
        if col.button(exemple, use_container_width=True):
            _poser(exemple)
            st.rerun()

# --- Saisie utilisateur ---
if question := st.chat_input("Pose ta question fiscale..."):
    _poser(question)
    st.rerun()
