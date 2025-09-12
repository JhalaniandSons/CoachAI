from groq import AsyncClient, AsyncGroq, Groq
import streamlit as st
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import os, asyncio

## chargement de l'environnement 
load_dotenv()
st.set_page_config(page_title="Coach Sportif IA", page_icon="🏋️")


#st.balloons()

#===================== STYLES CSS =================
st.markdown("""
<style>
/* Style pour le corps de la page (arrière-plan) */
.stApp {
    background-color: #0c0c0c; /* Une couleur plus foncée pour le fond */
    background-image: url("https://www.transparenttextures.com/patterns/clean-gray-paper.png");
    background-size: cover; 
    background-attachment: fixed;
}
/* Texte */
.card p {
    color: #CC8A27;
    font-size: 16px;
        }
/* Style pour les onglets (tabs) */
.stTabs [role="tab"] {
    background-color: #333333; 
    color: white; 
    border-radius: 10px 10px 0 0;
    border: none;
    margin: 0 5px;
    padding: 10px 20px;
    font-weight: bold;
}
.stTabs [role="tab"][aria-selected="true"] {
    background-color: #CC8A27;
    color: black;
}

/* Style pour les expanders (boîtes dépliables) */
.streamlit-expanderHeader {
    background-color: #444444;
    color: #CC8A27; 
    font-weight: bold;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid #CC8A27;
}

/* Style pour les boutons */
.stButton>button {
    background-color: #CC8A27;
    color: white;
    font-weight: bold;
    border-radius: 5px;
    border: none;
    padding: 10px 20px;
}
.stButton>button:hover {
    background-color: #a36d1f;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div lang="fr"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="card" lang="fr" style="text-align:center; margin-bottom:60px;">
    <h1 style="color:#CC8A27;">Welcome on <b>CoachAI 🏋️</b></h1>
</div>
            
<div style="text-align:center; margin-bottom:40px;">
    <h3 style="color:#CC8A27;">Prépare-toi à transformer ta vie !</h3>
    <h4 style="font-size:18px; color:#CC8A29;">
        <b>CoachAI</b> est ton partenaire dédié pour le sport, la nutrition et la récupération.<br>
        Ensemble, on va atteindre tes objectifs ! 💪🚀
    </h4>
</div>
          
""", unsafe_allow_html=True)

# ==================Cartes des fonctionnalités==================
features = [
    {
        "title": "📋 Plan d'entraînement sur mesure",
        "desc": "Adapté à votre niveau, vos objectifs et votre emploi du temps.",
        "color": "#3BE466"
    },
    {
        "title": "🏋️ Fiches d'exercices détaillées",
        "desc": "Instructions complètes pour une exécution parfaite avec variantes et matériel.",
        "color": "#84408A"
    },
    {
        "title": "📈 Suivi des progrès",
        "desc": "Visualisez vos performances et ajustez votre programme pour maximiser vos résultats.",
        "color": "#8A8E97"
    },
    {
        "title": "🥗 Nutrition & récupération",
        "desc": "Conseils personnalisés sur la nutrition, l’hydratation et la prévention des blessures.",
        "color": "#CC8A27"
    }
]

for feature in features:
    st.markdown(f"""
    <div lang="fr" style="background-color:{feature['color']}; padding:15px; border-radius:10px; margin-bottom:15px; border:1px solid #ccc;">
        <h3 style="margin:10;">{feature['title']}</h3>
        <p style="margin:5px 0 0 0; color:#333;">{feature['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<p style="text-align:center; font-size:16px; color:#1E90FF; margin-top:20px;">Prêt à commencer ? 🚀</p>', unsafe_allow_html=True)



# ============= 'MODÈLE DISPONIBLE'==========
model = st.sidebar.selectbox(
    "🏆 CHOOSE YOUR MODEL",
    ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "groq/compound","llama-3.3-70b-versatile"]
)

# ================ "DÉFINITION D'UN MENU"=========
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Plan d'entraînement", 
    "Banque d'exercices", 
    "Suivi des performances", 
    "Nutrition & Hydratation", 
    "Récupération & Prévention"
])

# stocker l'historique des échanges
if "history" not in st.session_state:
    st.session_state.history = []
if "plan_stage" not in st.session_state:
    st.session_state.plan_stage = 0
if "plan_data" not in st.session_state:
    st.session_state.plan_data = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

def next_stage():
    st.session_state.plan_stage += 1

def reset_plan():
    st.session_state.plan_stage = 0
    st.session_state.plan_data = {}

#========================STRUCTURE API =================

groq_api_key = st.secrets["API_KEY_GROQ"]

# Initialiser le client Groq (API OpenAI compatible)
client = AsyncOpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)
async def ask_model(system_prompt, user_message):
    messages = [{"role": "system", "content": system_prompt}]

    for h in st.session_state.history:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["Coach"]})
    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.6,
        max_completion_tokens=1024,
        stream=True,
        top_p=1.0,
        stop=None,
    )

    ##afficher les resultats en continu
    full_response = ""
    async for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
    # Accumuler le texte
    st.markdown(full_response)
    # Ajouter à l'historique
    st.session_state.history.append({
        "user": user_message,
        "Coach": full_response
    })

    return full_response

def process_user_input(prompt, user_message):
    with st.spinner("CoahAI ...."):
        return asyncio.run(ask_model(prompt, user_message))

# Inputs utilisateur
# === Logique des modules ===


with tab1:
    st.header("📋 Plan d'entraînement sur mesure")
    if st.session_state.plan_stage == 0:
        st.write("Bonjour ! Pour commencer, quel est ton principal objectif sportif ?")
        objectif = st.text_input("Ton objectif ?", key="objectif_input_step0")
        if st.button("Suivant", key="btn_step0"):
            if objectif:
                st.session_state.plan_data["objectif"] = objectif
                st.session_state.plan_stage = 1
                st.rerun()

    elif st.session_state.plan_stage == 1:
        st.write("Comment décrirais-tu ton niveau actuel ?")
        niveau = st.radio("Niveau", ["débutant", "intermédiaire", "avancé"], key="niveau_radio_step1")
        if st.button("Suivant", key="btn_step1"):
            st.session_state.plan_data["niveau"] = niveau
            st.session_state.plan_stage = 2
            st.rerun()

    elif st.session_state.plan_stage == 2:
        st.write("Pour quel sport ou quelle activité veux-tu un plan ?")
        sport = st.text_input("Sport pratiqué", "musculation", key="sport_input_step2")
        if st.button("Suivant", key="btn_step2"):
            st.session_state.plan_data["sport"] = sport
            st.session_state.plan_stage = 3
            st.rerun()

    elif st.session_state.plan_stage == 3:
        st.write("Combien de jours par semaine peux-tu t'entraîner et quelle est la durée idéale pour chaque séance ?")
        dispo = st.slider("Nombre de jours/semaine", 1, 7, 3, key="dispo_slider_step3")
        duree = st.slider("Durée par séance (minutes)", 15, 120, 45, key="duree_slider_step3")
        if st.button("Suivant", key="btn_step3"):
            st.session_state.plan_data["dispo"] = dispo
            st.session_state.plan_data["duree"] = duree
            st.session_state.plan_stage = 4
            st.rerun()

    elif st.session_state.plan_stage == 4:
        st.write("Pour terminer, quel matériel as-tu à ta disposition ?")
        materiel = st.text_input("Matériel disponible", "aucun", key="materiel_input_step4")
        if st.button("Generate Plan", key="btn_generate"):
            st.session_state.plan_data["materiel"] = materiel
            st.session_state.plan_stage = 5
            st.rerun()

    elif st.session_state.plan_stage == 5:
        data = st.session_state.plan_data
        st.info("Génération de votre plan d'entraînement... Veuillez patienter.")
        prompt = f"""En tant qu'expert dans le domaine sportif, en coaching et en suivi personnalisé, génère un plan d'entraînement structuré et détaillé pour 4 semaines basé sur les informations suivantes :
        - Objectif : {data['objectif']}
        - Niveau : {data['niveau']}
        - Sport : {data['sport']}
        - Disponibilité : {data['dispo']} jours/semaine, {data['duree']} min/séance
        - Matériel : {data['materiel']}
        Le plan doit inclure des séries, des répétitions, des temps de repos, et des conseils de progression. Utilise un format clair et lisible.
        """
        process_user_input(prompt, f"Plan d'entraînement pour {data['objectif']} ({data['niveau']}, {data['sport']})")

        if st.button("Nouveau plan", key="btn_restart"):
            reset_plan()
            st.rerun()

with tab2:
    st.header("🏋️ Fiches d'exercices détaillées")
    with st.expander("Cliquez pour chercher un exercice", expanded=True):
        exo = st.text_input("Quel exercice veux-tu apprendre ?", "squat")
        if st.button("Expliquer l'exercice", key="exo_btn"):
            prompt = f"En tant qu'expert dans le domaine sportif, le coaching et grand professeur de sport, Explique comment réaliser correctement {exo} avec étapes, erreurs à éviter, variantes, et matériel."
            process_user_input(prompt, f"Exercice pour t'améliorer :{exo} ")

with tab3:
    st.header("📈 Suivi des progrès")
    with st.expander("Cliquez pour suivre vos progrès", expanded=True):
        perf = st.text_area("Décris ta performance (ex: 'j’ai couru 5 km en 25 min')")
        if st.button("Analyser mes progrès", key="suivi_btn"):
            prompt = f"""Analyse cette performance et donne un feedback motivant et technique : {perf}
                        Félicite l'utilisateur s'il y a un progrès notable ou remarquable.
   
                     """
            process_user_input(prompt, f"Analyse de performance : {perf}")
with tab4:
    st.header("🥗 Nutrition & Hydratation")
    with st.expander("Cliquez pour des conseils", expanded=True):
        obj = st.text_input("Ton objectif sportif ?", "prise de masse")
        typ = st.text_input("Type d’entraînement ?", "musculation")
        if st.button("Conseils nutrition", key="nutri_btn"):
            prompt = f"Donne des conseils nutritionnels et hydratation adaptés à {obj} et {typ}."
            process_user_input(prompt, f"Nutrition pour {obj} - {typ}")

with tab5:
    st.header("🛌 Récupération & Prévention")
    with st.expander("Cliquez pour un plan de récupération", expanded=True):
        seance = st.text_input("Type de séance effectuée ?", "course intense")
        if st.button("Plan de récupération", key="recup_btn"):
            prompt = f"L’utilisateur a fait {seance}. Donne un plan de récupération avec étirements, sommeil, prévention blessures."
            process_user_input(prompt, f"Récupération après {seance}")


# =================="HISTORIQUE DES ÉCHANGES" ===================

st.sidebar.title("CoachAI")
chat_ids = [f"Chat {i+1}: {h['user'][:20]}..." for i, h in enumerate(st.session_state.history)]

selected = st.sidebar.radio("Conversations", ["Nouvelle conversation"] + chat_ids)

if selected != "Nouvelle conversation":
    idx = int(selected.split(":")[0].split(" ")[1]) - 1
    st.session_state.current_chat = idx
else:
    st.session_state.current_chat = None

# --- Affichage conversation courante ---
st.subheader("Conversation")
if st.session_state.current_chat is not None:
    chat = st.session_state.history[st.session_state.current_chat]
    st.markdown(f"**User :** {chat['user']}")
    st.markdown(f"**Coach :** {chat['Coach']}")
elif st.session_state.history:
    # Afficher la dernière conversation
    last_chat = st.session_state.history[-1]
    st.markdown(f"**User :** {last_chat['user']}")
    st.markdown(f"**Coach :** {last_chat['Coach']}")

st.markdown("N'hésitez pas à poser n'importe quelle question. Je suis là pour vous accompagner à chaque étape de votre parcours sportif.")


st.markdown(
    """
    <style>
    .stApp hr {
        border-color: #CC8A27
    }
    .stApp .css-1yv5y8n { 
        color: #f0f0f0 !important;
    }

    /* Style pour le lien GitHub */
    .stApp a {
        color: #3BE466
    }
    </style>
    <hr style="height:0px;border:none;color:#CC8A27;background-color:#CC8A27;" />
    <p style="text-align: center; color: #f0f0f0; font-size: 14px; margin-top: 10px;">🏋️ Crée par : <b>Eric KOULODJI</b> Version : <b>1.0</b>
        <a href="https://github.com/dona-eric/CoachAI" target="_blank" style="color: #3BE466; text-decoration: none;">GitHub</a>
    </p>
    """,
    unsafe_allow_html=True
)