"""
Premier test de l'assistant fiscal : un appel simple a Claude.
But : valider que la cle API et le SDK fonctionnent de bout en bout.
"""
import os
import sys

from dotenv import load_dotenv
import anthropic

# Evite les erreurs d'affichage des accents dans la console Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Charge les variables du fichier .env dans l'environnement
load_dotenv()

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("ERREUR : aucune cle API trouvee.")
    print("Ouvre le fichier .env et colle ta cle apres ANTHROPIC_API_KEY=")
    raise SystemExit(1)

# Le client lit automatiquement ANTHROPIC_API_KEY depuis l'environnement
client = anthropic.Anthropic()

reponse = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=400,
    system="Tu es un assistant fiscal pour le Cameroun. Reponds clairement et en francais.",
    messages=[
        {
            "role": "user",
            "content": "En une phrase simple, qu'est-ce que l'Attestation de Conformite Fiscale (ACF) au Cameroun ?",
        }
    ],
)

for bloc in reponse.content:
    if bloc.type == "text":
        print(bloc.text)
