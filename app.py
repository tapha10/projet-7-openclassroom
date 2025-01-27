import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pickle
import zipfile

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
    Ce tableau de bord est conçu pour être accessible et intelligible pour tous les utilisateurs.
    """
)

# Chargement des données
@st.cache_data
def load_data():
    with zipfile.ZipFile("cleaned_data.zip", "r") as z:
        with z.open("cleaned_data.csv") as f:
            return pd.read_csv(f)

@st.cache_data
def load_model():
    with open("model.pkl", "rb") as model_file:
        return pickle.load(model_file)

@st.cache_data
def load_model_columns():
    with open("model_columns.pkl", "rb") as columns_file:
        return pickle.load(columns_file)

# Charger les ressources
try:
    data = load_data()
    model = load_model()
    model_columns = load_model_columns()
    st.sidebar.success("Ressources chargées avec succès !")
except Exception as e:
    st.sidebar.error(f"Erreur lors du chargement des ressources : {e}")

# Interface utilisateur : Sélection d'un client
st.sidebar.header("Options Utilisateur")
client_id = st.sidebar.selectbox("Sélectionnez un ID Client :", data["SK_ID_CURR"].unique())

# Affichage des données du client
st.sidebar.subheader("Données Client")
client_data = data[data["SK_ID_CURR"] == client_id]
st.sidebar.dataframe(client_data)

# Visualisation du score et de sa probabilité
st.sidebar.subheader("Score de Crédit")
try:
    score = model.predict_proba(client_data[model_columns])[0, 1]  # Probabilité de la classe positive
    seuil = 0.5
    st.sidebar.metric("Score de Crédit", f"{score:.2f}")
    if score >= seuil:
        st.sidebar.success("Crédit Accordé")
    else:
        st.sidebar.error("Crédit Refusé")
except Exception as e:
    st.sidebar.error(f"Erreur lors de l'évaluation du score : {e}")

# Visualisation des principales informations descriptives
st.header("Informations Clés du Client")
st.subheader("Résumé des informations du client")
metrics = {
    "Revenu Annuel": client_data["AMT_INCOME_TOTAL"].values[0],
    "Montant Crédit": client_data["AMT_CREDIT"].values[0],
    "Type Contrat": client_data["NAME_CONTRACT_TYPE"].values[0]
}
for key, value in metrics.items():
    st.metric(key, value)

# Comparaison avec d'autres clients
st.header("Comparaison avec d'autres clients")
st.subheader("Filtrer par groupe")
genre = st.selectbox("Genre :", data["CODE_GENDER"].unique())
contrat = st.selectbox("Type de Contrat :", data["NAME_CONTRACT_TYPE"].unique())
filtered_data = data[(data["CODE_GENDER"] == genre) & (data["NAME_CONTRACT_TYPE"] == contrat)]
st.dataframe(filtered_data)

# Graphiques
st.header("Analyse des Revenus")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data["AMT_INCOME_TOTAL"], kde=True, bins=30, ax=ax, color="blue")
ax.axvline(client_data["AMT_INCOME_TOTAL"].values[0], color="red", linestyle="--", label="Client")
ax.set_title("Répartition des revenus")
ax.set_xlabel("Revenus")
ax.set_ylabel("Nombre de clients")
ax.legend()
st.pyplot(fig)

st.header("Montant des Crédits")
fig2 = px.box(
    data, x="NAME_CONTRACT_TYPE", y="AMT_CREDIT", color="NAME_CONTRACT_TYPE",
    title="Montants des crédits par type de contrat"
)
st.plotly_chart(fig2)

st.header("Relation Revenu-Crédit")
fig3 = px.scatter(
    data, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", color="CODE_GENDER",
    title="Revenu vs Crédit"
)
st.plotly_chart(fig3)

st.header("Répartition des Statuts Familiaux")
fig4 = px.pie(
    data, names="NAME_FAMILY_STATUS", title="Répartition des statuts familiaux"
)
st.plotly_chart(fig4)

st.markdown("**Merci d'utiliser le Dashboard Crédit Scoring !**")

