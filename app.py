import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import zipfile

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Crédit Scoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Dashboard Crédit Scoring")
st.markdown(
    """
    **Bienvenue sur le tableau de bord Crédit Scoring !**  
    Explorez les scores de crédit des clients et découvrez leur décision d'accord ou de refus en fonction des critères clés.
    """
)

# Chargement des données
@st.cache
def load_data():
    with zipfile.ZipFile("cleaned_data.zip", "r") as z:
        with z.open("cleaned_data.csv") as f:
            return pd.read_csv(f)

data = load_data()

st.sidebar.success("Données chargées avec succès !")

# Seuils basés sur l'analyse
SEUILS = {
    "AGE": 40,
    "YEARS_EMPLOYED": 5,
    "REGION_RATING_CLIENT_W_CITY": 2,
    "DAYS_LAST_PHONE_CHANGE": 900
}

# Calcul de la décision basée sur ces seuils
def check_credit_approval(client_row):
    age = -client_row["DAYS_BIRTH"] // 365
    years_employed = -client_row["DAYS_EMPLOYED"] // 365 if client_row["DAYS_EMPLOYED"] < 0 else 0
    region_rating = client_row["REGION_RATING_CLIENT_W_CITY"]
    phone_change_days = -client_row["DAYS_LAST_PHONE_CHANGE"]

    # Vérification des conditions
    if (age >= SEUILS["AGE"] and years_employed >= SEUILS["YEARS_EMPLOYED"] and
        region_rating <= SEUILS["REGION_RATING_CLIENT_W_CITY"] and phone_change_days >= SEUILS["DAYS_LAST_PHONE_CHANGE"]):
        return "Accordé", 0.8
    else:
        return "Refusé", 0.2

# Sélection de l'ID Client
st.sidebar.header("Options Utilisateur")
client_id = st.sidebar.selectbox("Sélectionnez un ID Client :", data["SK_ID_CURR"].unique())
client_data = data[data["SK_ID_CURR"] == client_id]

# Affichage du résultat
decision, score = check_credit_approval(client_data.iloc[0])
st.header("Résultat de l'évaluation")
st.write(f"### Décision : {decision}")

# Visualisation du score
fig, ax = plt.subplots(figsize=(8, 2))
ax.barh(["Score"], [score], color="green" if score >= 0.5 else "red", label="Score actuel")
ax.axvline(0.5, color="blue", linestyle="--", label="Seuil")
ax.set_xlim(0, 1)
ax.set_title("Score et Proximité du Seuil")
ax.legend()
ax.text(score, 0, f"{score:.2f}", va="center", ha="center", color="white", fontsize=12)
st.pyplot(fig)

# Affichage des valeurs des features importantes
st.header("Informations Clés du Client")
st.write("### Caractéristiques importantes")
important_features = ["DAYS_BIRTH", "DAYS_EMPLOYED", "CODE_GENDER", "REGION_RATING_CLIENT_W_CITY", "DAYS_LAST_PHONE_CHANGE", "NAME_EDUCATION_TYPE"]

for feature in important_features:
    st.write(f"**{feature}** : {client_data[feature].values[0]}")

# Comparaison du client avec un groupe similaire
st.header("Comparaison avec un Groupe")

# Filtrer les clients du même genre et niveau d'éducation
group_data = data[
    (data["CODE_GENDER"] == client_data.iloc[0]["CODE_GENDER"]) &
    (data["NAME_EDUCATION_TYPE"] == client_data.iloc[0]["NAME_EDUCATION_TYPE"])
]

# Création des visualisations
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Distribution de l'âge
client_age = -client_data.iloc[0]["DAYS_BIRTH"] // 365
ages = -group_data["DAYS_BIRTH"] // 365
axes[0].hist(ages, bins=20, alpha=0.6, color="blue", label="Groupe")
axes[0].axvline(client_age, color="red", linestyle="--", label="Client Sélectionné")
axes[0].set_title("Distribution de l'Âge")
axes[0].set_xlabel("Âge (années)")
axes[0].set_ylabel("Nombre de clients")
axes[0].legend()


# Affichage des visualisations
plt.tight_layout()
st.pyplot(fig)

st.markdown("**Merci d'utiliser le Dashboard Crédit Scoring !**")
