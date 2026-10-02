import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
# ==========================================================
# MOTEUR EXPERT DE COMMENTAIRE COMITE
# ==========================================================

def generate_expert_committee_commentary(score_df):

    commentaires = {
        "Synthese": [],
        "Forces": [],
        "Vigilances": [],
        "Recommandations": []
    }

    nb_fonds = len(score_df)

    score_moyen = score_df["Score"].mean()
    score_max = score_df["Score"].max()
    score_min = score_df["Score"].min()

    leader = score_df.iloc[0]["OPCVM"]
    leader_score = score_df.iloc[0]["Score"]

    dispersion = score_max - score_min

    # --------------------------------------------------
    # SYNTHESE
    # --------------------------------------------------

    commentaires["Synthese"].append(
        f"L'univers analysé comprend {nb_fonds} OPCVM présentant un score moyen de {score_moyen:.3f}."
    )

    commentaires["Synthese"].append(
        f"Le fonds le mieux classé est {leader} avec un score de {leader_score:.3f}."
    )

    if score_moyen >= 0.70:
        commentaires["Synthese"].append(
            "Le niveau moyen des notations traduit globalement une qualité satisfaisante de l'univers analysé."
        )

    elif score_moyen >= 0.50:
        commentaires["Synthese"].append(
            "Les résultats mettent en évidence une qualité globalement moyenne avec des situations contrastées selon les fonds."
        )

    else:
        commentaires["Synthese"].append(
            "L'univers présente globalement des scores faibles nécessitant une analyse approfondie des déterminants de performance."
        )

    # --------------------------------------------------
    # FORCES
    # --------------------------------------------------

    if dispersion < 0.30:
        commentaires["Forces"].append(
            "Le classement présente une bonne homogénéité entre les OPCVM analysés."
        )

    if score_max >= 0.80:
        commentaires["Forces"].append(
            "Les meilleurs fonds affichent un niveau de score élevé traduisant un positionnement particulièrement favorable."
        )

    top3 = score_df.head(3)

    commentaires["Forces"].append(
        f"Les fonds les mieux classés sont : {', '.join(top3['OPCVM'].astype(str).tolist())}."
    )

    if score_moyen > 0.60:
        commentaires["Forces"].append(
            "La majorité des fonds affiche un niveau de notation compatible avec les standards attendus par un investisseur institutionnel."
        )

    # --------------------------------------------------
    # VIGILANCES
    # --------------------------------------------------

    if dispersion > 0.50:
        commentaires["Vigilances"].append(
            "La forte dispersion des scores traduit une hétérogénéité importante des profils de qualité au sein de l'univers analysé."
        )

    if score_min < 0.30:
        commentaires["Vigilances"].append(
            "Certains fonds affichent des scores sensiblement inférieurs à la moyenne nécessitant une revue détaillée."
        )

    fonds_faibles = score_df.tail(min(3, len(score_df)))

    commentaires["Vigilances"].append(
        f"Une attention particulière devrait être portée aux fonds suivants : {', '.join(fonds_faibles['OPCVM'].astype(str).tolist())}."
    )

    # --------------------------------------------------
    # RECOMMANDATIONS
    # --------------------------------------------------

    commentaires["Recommandations"].append(
        "Privilégier une analyse détaillée des fonds situés dans le premier quartile du classement."
    )

    commentaires["Recommandations"].append(
        "Compléter l'analyse quantitative par une revue qualitative du processus de gestion et du dispositif de maîtrise des risques."
    )

    commentaires["Recommandations"].append(
        "Mettre en place un suivi régulier des fonds situés en bas du classement afin d'identifier l'évolution de leurs fondamentaux."
    )

    return commentaires
``
# ----------------------------------------------------
# CONFIGURATION PAGE
# ----------------------------------------------------
st.set_page_config(
    page_title="OPCVM Scoring Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 OPCVM SCORING DASHBOARD")
st.markdown("Classement dynamique des OPCVM")

# ----------------------------------------------------
# FONCTION NORMALISATION
# ----------------------------------------------------
def normalize(series):

    if series.max() == series.min():
        return 1

    return (series - series.min()) / (series.max() - series.min())

# ----------------------------------------------------
# CHARGEMENT FICHIER
# ----------------------------------------------------
uploaded_file = st.file_uploader(
    "Charger le fichier Excel OPCVM",
    type=["xlsx"]
)

if uploaded_file is None:

    st.info("Veuillez charger le fichier Excel.")

    st.stop()

# ----------------------------------------------------
# LECTURE EXCEL
# ----------------------------------------------------
try:

    df = pd.read_excel(
        uploaded_file,
        sheet_name="Base_OPCVM"
    )

    param_df = pd.read_excel(
        uploaded_file,
        sheet_name="Parametres"
    )

except Exception as e:

    st.error(f"Erreur de lecture : {e}")
    st.stop()

st.success("Fichier chargé avec succès")

# ----------------------------------------------------
# PARAMETRES
# ----------------------------------------------------
st.sidebar.header("⚙️ Poids des critères")

default_weights = {}

for _, row in param_df.iterrows():

    default_weights[row["Critere"]] = float(row["Poids"])

poids_an = st.sidebar.slider(
    "Actif Net (AN)",
    0.0,
    1.0,
    float(default_weights.get("AN", 0.20)),
    0.05
)

poids_frais = st.sidebar.slider(
    "Frais de gestion",
    0.0,
    1.0,
    float(default_weights.get("Frais de gestion", 0.20)),
    0.05
)

poids_ytd = st.sidebar.slider(
    "Performance YTD",
    0.0,
    1.0,
    float(default_weights.get("Perf_YTD", 0.35)),
    0.05
)

poids_semaine = st.sidebar.slider(
    "Performance 1 semaine",
    0.0,
    1.0,
    float(default_weights.get("Perf_1_ semaine", 0.25)),
    0.05
)

poids_mois = st.sidebar.slider(
    "Performance 1 mois",
    0.0,
    1.0,
    float(default_weights.get("Perf_1_ mois", 0.00)),
    0.05
)

poids_total = (
    poids_an
    + poids_frais
    + poids_ytd
    + poids_semaine
    + poids_mois
)

st.sidebar.metric(
    "Somme des poids",
    round(poids_total, 2)
)

if poids_total == 0:

    st.error("La somme des poids ne peut pas être nulle.")
    st.stop()

# ----------------------------------------------------
# NORMALISATION
# ----------------------------------------------------
score_df = df.copy()

score_df["AN_norm"] = normalize(score_df["AN"])

score_df["Frais_norm"] = (
    score_df["Frais de gestion"].max()
    - score_df["Frais de gestion"]
)

score_df["Frais_norm"] = normalize(
    score_df["Frais_norm"]
)

score_df["YTD_norm"] = normalize(
    score_df["Perf_YTD"]
)

score_df["Semaine_norm"] = normalize(
    score_df["Perf_1_ semaine"]
)

score_df["Mois_norm"] = normalize(
    score_df["Perf_1_ mois"]
)

# ----------------------------------------------------
# SCORE GLOBAL
# ----------------------------------------------------
score_df["Score"] = (

    score_df["AN_norm"] * poids_an

    + score_df["Frais_norm"] * poids_frais

    + score_df["YTD_norm"] * poids_ytd

    + score_df["Semaine_norm"] * poids_semaine

    + score_df["Mois_norm"] * poids_mois

) / poids_total

score_df = score_df.sort_values(
    by="Score",
    ascending=False
)

score_df["Rang"] = range(
    1,
    len(score_df) + 1
)

# ----------------------------------------------------
# KPI
# ----------------------------------------------------
c1, c2, c3 = st.columns(3)

c1.metric(
    "Nombre OPCVM",
    len(score_df)
)

c2.metric(
    "Meilleur score",
    round(score_df["Score"].max(), 3)
)

c3.metric(
    "OPCVM N°1",
    score_df.iloc[0]["OPCVM"]
)

# ----------------------------------------------------
# TABLEAU CLASSEMENT
# ----------------------------------------------------
st.subheader("🏆 Classement Général")

st.dataframe(
    score_df[
        [
            "Rang",
            "OPCVM",
            "Score"
        ]
    ],
    use_container_width=True
)

# ----------------------------------------------------
# TOP 10 BAR CHART
# ----------------------------------------------------
st.subheader("📊 Top 10 OPCVM")

fig_bar = px.bar(
    score_df.head(10),
    x="OPCVM",
    y="Score",
    color="Score",
    text="Score"
)

fig_bar.update_layout(
    height=500
)

st.plotly_chart(
    fig_bar,
    use_container_width=True
)

# ----------------------------------------------------
# RADAR
# ----------------------------------------------------
st.subheader("🕸️ Radar Comparatif")

selection = st.multiselect(
    "Choisir des OPCVM",
    score_df["OPCVM"],
    default=list(score_df.head(3)["OPCVM"])
)

if len(selection) > 0:

    radar_df = score_df[
        score_df["OPCVM"].isin(selection)
    ]

    fig_radar = go.Figure()

    categories = [
        "AN_norm",
        "Frais_norm",
        "YTD_norm",
        "Semaine_norm",
        "Mois_norm"
    ]

    labels = [
        "Taille",
        "Frais",
        "Perf YTD",
        "Perf Semaine",
        "Perf Mois"
    ]

    for _, row in radar_df.iterrows():

        values = [
            row["AN_norm"],
            row["Frais_norm"],
            row["YTD_norm"],
            row["Semaine_norm"],
            row["Mois_norm"]
        ]

        values += [values[0]]

        fig_radar.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels + [labels[0]],
                fill="toself",
                name=row["OPCVM"]
            )
        )

    fig_radar.update_layout(
        height=700,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        )
    )

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )

# ----------------------------------------------------
# HEATMAP
# ----------------------------------------------------
st.subheader("🔥 Heatmap des Critères")

heatmap = score_df.head(20).set_index("OPCVM")[[
    "AN_norm",
    "Frais_norm",
    "YTD_norm",
    "Semaine_norm",
    "Mois_norm",
    "Score"
]]

fig_heat = px.imshow(
    heatmap,
    text_auto=".2f",
    color_continuous_scale="RdYlGn",
    aspect="auto"
)

fig_heat.update_layout(
    height=700
)

st.plotly_chart(
    fig_heat,
    use_container_width=True
)

# ----------------------------------------------------
# EXPORT EXCEL
# ----------------------------------------------------
st.subheader("📥 Export Excel")

buffer = BytesIO()

with pd.ExcelWriter(
    buffer,
    engine="xlsxwriter"
) as writer:

    score_df.to_excel(
        writer,
        index=False,
        sheet_name="Classement"
    )

st.download_button(
    label="Télécharger le classement",
    data=buffer.getvalue(),
    file_name="Classement_OPCVM.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ----------------------------------------------------
# DONNEES DETAILLEES
# ----------------------------------------------------
with st.expander("Afficher toutes les données"):

    st.dataframe(
        score_df,
        use_container_width=True
    )
