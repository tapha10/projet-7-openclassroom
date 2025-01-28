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
        
# Déterminer la proximité au seuil pour chaque règle
    accord_distance = [
        max(0, (rule["value"] - income) if rule["operator"] == ">=" else (credit - rule["value"]))
        for rule in RULES["ACCORD"]
    ]
    refus_distance = [
        max(0, (rule["value"] - income) if rule["operator"] == "<" else (credit - rule["value"]))
        for rule in RULES["REFUS"]
    ]

    # Décision et score basé sur les distances aux règles
    if all(d == 0 for d in accord_distance):
        return "Accordé", 0.8  # Score élevé pour un accord
    elif any(d > 0 for d in refus_distance):
        return "Refusé", 0.2  # Score bas pour un refus
    else:
        return "Refusé", 0.5  # Cas limite au seuil

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

    fig, ax = plt.subplots(figsize=(5, 3))
    gauge(arrow=score, ax=ax, title="Niveau de Risque", colors="RdYlGn" if decision == "Accordé" else "RdYlGn_r")
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

