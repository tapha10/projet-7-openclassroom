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

@st.cache
def load_model_columns():
    with open("model_columns.pkl", "rb") as columns_file:
        return pickle.load(columns_file)

# Charger les données
try:
    data = load_data()
    st.sidebar.success("Données chargées avec succès !")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement des données : {e}")

# Fonction pour jauge
def gauge(arrow=0.4, labels=['Faible', 'Modéré', 'Élevé', 'Très élevé'],
          title='', min_val=0, max_val=1, threshold=0.5,
          colors='RdYlGn_r', ax=None, figsize=(2, 1.3)):
    N = len(labels)
    cmap = cm.get_cmap(colors, N)
    colors = cmap(np.arange(N))[::-1]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    for i, color in enumerate(colors):
        ax.add_patch(Wedge((0., 0.), .4, i * 180 / N, (i + 1) * 180 / N, width=0.10, facecolor=color))

    ax.add_patch(Rectangle((-0.4, -0.1), 0.8, 0.1, facecolor='w', lw=2))
    ax.text(0, -0.1, title, horizontalalignment='center', verticalalignment='center', fontsize=15)

    pos = 180 - (180 * (arrow - min_val) / (max_val - min_val))
    ax.arrow(0, 0, 0.2 * np.cos(np.radians(pos)), 0.2 * np.sin(np.radians(pos)), width=0.02, head_width=0.05, head_length=0.05, fc='k')
    ax.add_patch(Circle((0, 0), radius=0.02, facecolor='k'))

    ax.set_frame_on(False)
    ax.axes.set_xticks([])
    ax.axes.set_yticks([])
    ax.axis('equal')
    return ax

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

    fig, ax = plt.subplots(figsize=(5, 3))
    gauge(arrow=score, ax=ax, title="Niveau de Risque")
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

# Visualisation de l'importance des variables
st.header("Importance des Variables Globale")
try:
    df_feature_importance = data[["DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_EMPLOYED", "REGION_RATING_CLIENT_W_CITY", "REGION_RATING_CLIENT"]].mean().sort_values(ascending=False)

    plt.figure(figsize=(8, 6))
    sns.barplot(x=df_feature_importance.values, y=df_feature_importance.index, color="skyblue")
    plt.title("Importance des Variables (EXT Sources)")
    plt.xlabel("Importance Moyenne")
    plt.ylabel("Variable")
    st.pyplot(plt.gcf())
except Exception as e:
    st.error(f"Erreur lors de l'affichage des importances des variables : {e}")
