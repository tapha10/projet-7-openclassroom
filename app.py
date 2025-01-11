import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

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
    Explorez les données de modélisation et découvrez les prédictions de score de crédit.  
    Ce tableau de bord est conçu pour répondre aux besoins des utilisateurs, y compris ceux en situation de handicap, conformément aux critères WCAG.  
    """
)

# Chargement des données
@st.cache
def load_data():
    return pd.read_csv("cleaned_data.csv")

data = load_data()

# Interface utilisateur : Sélection d'un client
st.sidebar.header("Options Utilisateur")
client_id = st.sidebar.selectbox("Sélectionnez un ID Client :", data["SK_ID_CURR"].unique())

# Affichage des données du client
st.sidebar.subheader("Données Client")
client_data = data[data["SK_ID_CURR"] == client_id]
st.sidebar.dataframe(client_data)

# Graphique 1 : Distribution des revenus
st.header("Analyse des Revenus des Clients")
st.subheader("Répartition des revenus annuels")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data["AMT_INCOME_TOTAL"], kde=True, bins=30, color="blue", ax=ax)
ax.set_title("Répartition des revenus annuels", fontsize=16)
ax.set_xlabel("Revenus annuels", fontsize=14)
ax.set_ylabel("Nombre de clients", fontsize=14)
st.pyplot(fig)

# Graphique 2 : Analyse des crédits par type de contrat
st.header("Analyse des Crédits")
st.subheader("Montants des crédits par type de contrat")
fig2 = px.box(
    data,
    x="NAME_CONTRACT_TYPE",
    y="AMT_CREDIT",
    color="NAME_CONTRACT_TYPE",
    title="Montants des crédits par type de contrat",
    labels={"NAME_CONTRACT_TYPE": "Type de Contrat", "AMT_CREDIT": "Montant du Crédit"},
)
st.plotly_chart(fig2)

# Graphique 3 : Relation entre le revenu et le montant du crédit
st.header("Relation entre Revenu et Crédit")
st.subheader("Analyse bi-variée : Revenu vs Montant du Crédit")
fig3 = px.scatter(
    data,
    x="AMT_INCOME_TOTAL",
    y="AMT_CREDIT",
    color="CODE_GENDER",
    labels={"AMT_INCOME_TOTAL": "Revenu Annuel", "AMT_CREDIT": "Montant du Crédit"},
    title="Revenu vs Montant du Crédit par Genre",
)
st.plotly_chart(fig3)

# Graphique 4 : Proportions des statuts familiaux
st.header("Analyse des Statuts Familiaux")
st.subheader("Proportions des différents statuts familiaux")
fig4 = px.pie(
    data,
    names="NAME_FAMILY_STATUS",
    title="Répartition des statuts familiaux",
    hole=0.4
)
st.plotly_chart(fig4)

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

fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(x=feature_x, y=feature_y, data=data, alpha=0.6)
st.pyplot(fig)
