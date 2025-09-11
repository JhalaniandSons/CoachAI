from groq import AsyncClient, AsyncGroq, Groq
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

## chargement de l'environnement 
load_dotenv()
groq_api_key = st.secrets["API_KEY_GROQ"]

# Initialiser le client Groq (API OpenAI compatible)
client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

st.set_page_config(page_title="Coach Sportif IA", page_icon="🏋️")

st.title("Bienvenue sur CoachAI 🏋️")

st.markdown("""
Bonjour ! Je suis **CoachAI**, votre assistant personnel en matière de sport et de bien-être.

Que vous soyez un athlète chevronné ou que vous commenciez tout juste votre parcours, je suis là pour vous aider à atteindre vos objectifs.

Je peux :
* **Créer un plan d'entraînement sur mesure** : adapté à votre niveau, vos objectifs et votre emploi du temps.
* **Fournir des fiches d'exercices détaillées** : avec des instructions pour une exécution parfaite.
* **Suivre vos progrès** : et ajuster votre programme pour maximiser vos résultats.
* **Répondre à toutes vos questions** : sur la nutrition, la récupération, la prévention des blessures, et bien plus encore.

Prêt à commencer ?
""")



# ============= 'MODÈLE DISPONIBLE'==========
model = st.selectbox(
    "🤖 Choisis ton modèle Groq",
    ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "openai/gpt-oss-120b", "deepseek-r1-distill-llama-70b"]
)

# ================ "DÉFINITION D'UN MENU"=========
menu = st.sidebar.radio("📌 Choisis une section :", [
    "Plan d'entraînement",
    "Banque d'exercices",
    "Suivi des performances",
    "Nutrition & Hydratation",
    "Récupération & Prévention"
])

# stocker l'historique des échanges
if "history" not in st.session_state:
    st.session_state.history = []
def ask_model(system_prompt, user_message):
    messages = [{"role": "system", "content": system_prompt}]

    for h in st.session_state.history:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["Coach"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.6,
        max_completion_tokens=1024,
        stream=True,
        top_p=1.0,
    )

    # Accumuler le texte
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
    st.markdown(full_response)
    # Ajouter à l'historique
    st.session_state.history.append({
        "user": user_message,
        "Coach": full_response
    })

    return full_response

def process_user_input(prompt, user_message):
    return ask_model(prompt, user_message)

# Inputs utilisateur
# === Logique des modules ===
if menu == "Plan d'entraînement":
    objectif = st.text_input("Ton objectif ?", "perte de poids")
    niveau = st.radio("Niveau", ["débutant", "intermédiaire", "avancé"])
    sport = st.text_input("Sport pratiqué", "musculation")
    dispo = st.slider("Nombre de jours/semaine", 1, 7, 3)
    duree = st.slider("Durée par séance (minutes)", 15, 120, 45)
    materiel = st.text_input("Matériel disponible", "aucun")

    if st.button("Générer mon plan"):
        prompt = f"""En tant qu'expert dans le domaine sportif, en coaching et en suivi personnalisé. 
        Génère un plan structuré pour :
        - Objectif : {objectif}
        - Niveau : {niveau}
        - Sport : {sport}
        - Disponibilité : {dispo} jours/semaine, {duree} min/séance
        - Matériel : {materiel}
        """
        process_user_input(prompt, f"Plan d'entraînement pour {objectif} ({niveau}, {sport})")

elif menu == "Banque d'exercices":
    exo = st.text_input("Quel exercice veux-tu apprendre ?", "squat")
    if st.button("Expliquer l'exercice"):
        prompt = f"En tant qu'expert dans le domaine sportif, le coaching et grand professeur de sport,Explique comment réaliser correctement {exo} avec étapes, erreurs à éviter, variantes, et matériel."
        process_user_input(prompt, f"Exercice pour t'améliorer :{exo} ")

elif menu == "Suivi des performances":
    perf = st.text_area("Décris ta performance (ex: 'j’ai couru 5 km en 25 min')")
    if st.button("Analyser mes progrès"):
        prompt = f"Analyse cette performance et donne un feedback motivant : {perf}"
        process_user_input(prompt, f"Analyse de performance : {perf}")

elif menu == "Nutrition & Hydratation":
    obj = st.text_input("Ton objectif sportif ?", "prise de masse")
    typ = st.text_input("Type d’entraînement ?", "musculation")
    if st.button("Conseils nutrition"):
        prompt = f"Donne des conseils nutritionnels et hydratation adaptés à {obj} et {typ}."
        process_user_input(prompt, f"Nutrition pour {obj} - {typ}")

elif menu == "Récupération & Prévention":
    seance = st.text_input("Type de séance effectuée ?", "course intense")
    if st.button("Plan de récupération"):
        prompt = f"L’utilisateur a fait {seance}. Donne un plan de récupération avec étirements, sommeil, prévention blessures."
        process_user_input(prompt, f"Récupération après {seance}")


# =================="HISTORIQUE DES ÉCHANGES" ===================
st.subheader("💬 HISTORYQUE")
for chat in st.session_state.history:
    st.markdown(f"**Vous:** {chat['user']}")
    st.markdown(f"**CoachAI:** {chat['Coach']}")

st.markdown("N'hésitez pas à poser n'importe quelle question. Je suis là pour vous accompagner à chaque étape de votre parcours sportif.")
