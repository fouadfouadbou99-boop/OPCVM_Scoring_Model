import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Scoring Dynamique OPCVM",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Scoring Dynamique OPCVM")

# --------------------------------------------------
# Chargement fichier
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Charger le fichier Excel OPCVM",
    type=["xlsx"]
)

if uploaded_file is not None:

    # Lecture des feuilles
    df_base = pd.read_excel(uploaded_file, sheet_name="Base_OPCVM")
    df_param = pd.read_excel(uploaded_file, sheet_name="Parametres")

    st.success("Fichier chargé avec succès")

    st.subheader("Base OPCVM")
    st.dataframe(df_base)

    # --------------------------------------------------
    # Récupération poids
    # --------------------------------------------------
    poids_dict = dict(
        zip(df_param["Critere"], df_param["Poids"])
    )

    st.sidebar.header("Paramètres de scoring")

    poids_an = st.sidebar.slider(
        "Poids AN",
        0.0,
        1.0,
        float(poids_dict.get("AN", 0.20)),
        0.05
    )

    poids_frais = st.sidebar.slider(
        "Poids Frais de gestion",
        0.0,
        1.0,
        float(poids_dict.get("Frais de gestion", 0.20)),
        0.05
    )

    poids_ytd = st.sidebar.slider(
        "Poids Perf_YTD",
        0.0,
        1.0,
        float(poids_dict.get("Perf_YTD", 0.35)),
        0.05
    )

    poids_sem = st.sidebar.slider(
        "Poids Perf_1_ semaine",
        0.0,
        1.0,
        float(poids_dict.get("Perf_1_ semaine", 0.25)),
        0.05
    )

    poids_mois = st.sidebar.slider(
        "Poids Perf_1_ mois",
        0.0,
        1.0,
        float(poids_dict.get("Perf_1_ mois", 0.00)),
        0.05
    )

    total = (
        poids_an +
        poids_frais +
        poids_ytd +
        poids_sem +
        poids_mois
    )

    st.sidebar.metric("Total poids", round(total, 4))

    if total == 0:
        st.error("La somme des poids doit être supérieure à zéro.")
        st.stop()

    # --------------------------------------------------
    # Normalisation Min-Max
    # --------------------------------------------------

    score_df = df_base.copy()

    # Critère bénéfique : AN
    score_df["AN_norm"] = (
        (score_df["AN"] - score_df["AN"].min())
        /
        (score_df["AN"].max() - score_df["AN"].min())
    )

    # Critère coût : Frais de gestion (inverse)
    score_df["Frais_norm"] = (
        (score_df["Frais de gestion"].max() - score_df["Frais de gestion"])
        /
        (
            score_df["Frais de gestion"].max()
            - score_df["Frais de gestion"].min()
        )
    )

    # Critères bénéfices
    score_df["YTD_norm"] = (
        (score_df["Perf_YTD"] - score_df["Perf_YTD"].min())
        /
        (score_df["Perf_YTD"].max() - score_df["Perf_YTD"].min())
    )

    score_df["Semaine_norm"] = (
        (score_df["Perf_1_ semaine"] - score_df["Perf_1_ semaine"].min())
        /
        (
            score_df["Perf_1_ semaine"].max()
            - score_df["Perf_1_ semaine"].min()
        )
    )

    score_df["Mois_norm"] = (
        (score_df["Perf_1_ mois"] - score_df["Perf_1_ mois"].min())
        /
        (
            score_df["Perf_1_ mois"].max()
            - score_df["Perf_1_ mois"].min()
        )
    )

    # --------------------------------------------------
    # Score pondéré
    # --------------------------------------------------

    score_df["Score"] = (
        poids_an * score_df["AN_norm"]
        + poids_frais * score_df["Frais_norm"]
        + poids_ytd * score_df["YTD_norm"]
        + poids_sem * score_df["Semaine_norm"]
        + poids_mois * score_df["Mois_norm"]
    ) / total

    # Classement
    score_df["Rang"] = (
        score_df["Score"]
        .rank(ascending=False, method="dense")
        .astype(int)
    )

    score_df = score_df.sort_values(
        "Score",
        ascending=False
    )

    st.subheader("Classement OPCVM")

    st.dataframe(
        score_df[
            [
                "OPCVM",
                "Score",
                "Rang",
                "AN",
                "Frais de gestion",
                "Perf_YTD",
                "Perf_1_ semaine",
                "Perf_1_ mois"
            ]
        ],
        use_container_width=True
    )

    # --------------------------------------------------
    # TOP 10
    # --------------------------------------------------

    st.subheader("🏆 Top 10 OPCVM")

    st.dataframe(
        score_df.head(10)[
            ["Rang", "OPCVM", "Score"]
        ],
        use_container_width=True
    )

    # --------------------------------------------------
    # Graphique
    # --------------------------------------------------

    st.subheader("Visualisation des scores")

    st.bar_chart(
        score_df.set_index("OPCVM")["Score"].head(15)
    )

    # --------------------------------------------------
    # Export Excel
    # --------------------------------------------------

    export_df = score_df.copy()

    output_file = "Scoring_OPCVM_Resultat.xlsx"

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        export_df.to_excel(
            writer,
            sheet_name="Scoring",
            index=False
        )

    with open(output_file, "rb") as f:
        st.download_button(
            label="📥 Télécharger le classement",
            data=f,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
