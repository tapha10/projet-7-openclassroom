import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pickle
import zipfile
import numpy as np
from matplotlib.patches import Wedge, Rectangle, Circle
from matplotlib import cm

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Crédit Scoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre et description
st.title("Dashboard Crédit Scoring")
st.markdown(
    """
    **Bienvenue sur le tableau de bord Crédit Scoring !**  
    Explorez les scores de crédit des clients et découvrez leur décision d'accord ou de refus.  
    """
)

# Chargement des données
@st.cache
def load_data():
    with zipfile.ZipFile("cleaned_data.zip", "r") as z:
        with z.open("cleaned_data.csv") as f:
            return pd.read_csv(f)

# Charger les données
try:
    data = load_data()
    st.sidebar.success("Données chargées avec succès !")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement des données : {e}")

# Définir les règles pour accorder ou refuser un crédit
RULES = {
    "ACCORD": [
        {"feature": "AMT_INCOME_TOTAL", "operator": ">=", "value": 50000},
        {"feature": "AMT_CREDIT", "operator": "<=", "value": 500000},
    ],
    "REFUS": [
        {"feature": "AMT_INCOME_TOTAL", "operator": "<", "value": 20000},
        {"feature": "AMT_CREDIT", "operator": ">", "value": 1000000},
    ]
}

# Vérifier si un client satisfait les règles et calculer le seuil
def check_decision_and_calculate_threshold(client_row):
    income = client_row["AMT_INCOME_TOTAL"]
    credit = client_row["AMT_CREDIT"]

    accord_distance = [
        max(0, (rule["value"] - income) if rule["operator"] == ">=" else (credit - rule["value"]))
        for rule in RULES["ACCORD"]
    ]
    refus_distance = [
        max(0, (rule["value"] - income) if rule["operator"] == "<" else (credit - rule["value"]))
        for rule in RULES["REFUS"]
    ]

    if all(d == 0 for d in accord_distance):
        return "Accordé", 0.8
    elif any(d > 0 for d in refus_distance):
        return "Refusé", 0.2
    else:
        return "Refusé", 0.5

# Interface utilisateur : Sélection d'un client
st.sidebar.header("Options Utilisateur")
client_id = st.sidebar.selectbox("Sélectionnez un ID Client :", data["SK_ID_CURR"].unique())

# Visualisation du Score et de la Proximité avec le Seuil
st.header("Visualisation du Score et de la Proximité avec le Seuil")
client_data = data[data["SK_ID_CURR"] == client_id]
try:
    decision, score = check_decision_and_calculate_threshold(client_data.iloc[0])
    seuil = 0.5
    st.write(f"### Résultat pour le client sélectionné : {decision}")

    # Visualisation du score et de sa proximité avec le seuil
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.barh(["Score"], [score], color="green" if score >= seuil else "red", label="Score actuel")
    ax.axvline(seuil, color="blue", linestyle="--", label="Seuil")
    ax.set_xlim(0, 1)
    ax.set_title("Score et Proximité du Seuil")
    ax.legend()

    # Annotation du score
    ax.text(score, 0, f"{score:.2f}", va="center", ha="center", color="white", fontsize=12)

    st.pyplot(fig)

except Exception as e:
    st.error(f"Erreur lors de l'évaluation des règles : {e}")

# Visualisation des principales informations descriptives du client
st.header("Informations Clés du Client")
try:
    metrics = {
        "Revenu Annuel": client_data["AMT_INCOME_TOTAL"].values[0],
        "Montant Crédit": client_data["AMT_CREDIT"].values[0],
        "Type Contrat": client_data["NAME_CONTRACT_TYPE"].values[0]
    }
    for key, value in metrics.items():
        st.metric(key, value)
except Exception as e:
    st.error(f"Erreur lors de l'affichage des informations descriptives : {e}")

# Comparaison avec un groupe similaire
st.header("Comparaison avec un Groupe")
st.subheader("Comparer avec des clients similaires")
try:
    genre = st.selectbox("Genre :", data["CODE_GENDER"].unique())
    contrat = st.selectbox("Type de Contrat :", data["NAME_CONTRACT_TYPE"].unique())
    filtered_data = data[(data["CODE_GENDER"] == genre) & (data["NAME_CONTRACT_TYPE"] == contrat)]

    st.subheader("Visualisation des Revenus et Crédits")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        x="AMT_INCOME_TOTAL", y="AMT_CREDIT", data=filtered_data, label="Groupe", ax=ax, color="blue", alpha=0.6
    )
    ax.scatter(
        client_data["AMT_INCOME_TOTAL"], client_data["AMT_CREDIT"],
        color="red", label="Client Sélectionné", s=100
    )
    ax.set_title("Revenu vs Montant du Crédit")
    ax.set_xlabel("Revenu Annuel")
    ax.set_ylabel("Montant du Crédit")
    ax.set_xlim(0, 2.5)
    ax.legend()
    st.pyplot(fig)
except Exception as e:
    st.error(f"Erreur lors de la comparaison avec le groupe : {e}")

# Visualisation des variables les plus importantes pour le client sélectionné
st.header("Feature Importance pour le Client Sélectionné")
try:
    important_features = ["DAYS_BIRTH", "DAYS_EMPLOYED", "CODE_GENDER", "REGION_RATING_CLIENT_W_CITY", "DAYS_LAST_PHONE_CHANGE", "NAME_EDUCATION_TYPE"]
    feature_values = client_data[important_features].iloc[0]

    st.write("### Top 6 Variables les Plus Importantes :")
    for feature, value in feature_values.items():
        st.write(f"**{feature}** : {value}")

except Exception as e:
    st.error(f"Erreur lors de l'affichage des variables importantes : {e}")

# Critères d'accessibilité WCAG
st.markdown(
    """
    ### Accessibilité du Dashboard
    - **Critère 1.1.1 Contenu non textuel :** Les graphiques sont accompagnés de descriptions et de titres compréhensibles.
    - **Critère 1.4.1 Utilisation de la couleur :** Les graphiques utilisent des couleurs adaptées pour ne pas dépendre uniquement de la couleur.
    - **Critère 1.4.3 Contraste (minimum) :** Les contrastes entre le texte et l'arrière-plan respectent les normes.
    - **Critère 1.4.4 Redimensionnement du texte :** Utilisez le zoom du navigateur pour ajuster la taille du texte sans perte de lisibilité.
    - **Critère 2.4.2 Titre de page :** Le titre de la page est clair et décrit l'objectif du tableau de bord.
    """
)

# Message de fin
st.markdown("**Merci d'utiliser le Dashboard Crédit Scoring !**")


