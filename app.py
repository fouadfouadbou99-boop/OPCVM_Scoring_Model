import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(
    page_title="OPCVM Scoring Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 OPCVM Scoring Dashboard")

st.markdown(
    "Classement dynamique des OPCVM selon plusieurs critères."
)

uploaded_file = st.file_uploader(
    "Charger votre fichier Excel",
    type=["xlsx"]
)

if uploaded_file:

    try:

        df = pd.read_excel(
            uploaded_file,
            sheet_name="Base_OPCVM"
        )

        params = pd.read_excel(
            uploaded_file,
            sheet_name="Parametres"
        )

        st.success("Fichier chargé avec succès")

    except Exception as e:

        st.error(f"Erreur : {e}")
        st.stop()

    st.sidebar.header("⚙️ Paramètres")

    poids_reference = {

        row["Critere"]: row["Poids"]

        for _, row in params.iterrows()
    }

    poids_an = st.sidebar.slider(
        "AN",
        0.0,
        1.0,
        float(poids_reference.get("AN", 0.2)),
        0.05
    )

    poids_frais = st.sidebar.slider(
        "Frais",
        0.0,
        1.0,
        float(poids_reference.get("Frais de gestion", 0.2)),
        0.05
    )

    poids_ytd = st.sidebar.slider(
        "Performance YTD",
        0.0,
        1.0,
        float(poids_reference.get("Perf_YTD", 0.35)),
        0.05
    )

    poids_sem = st.sidebar.slider(
        "Performance 1 semaine",
        0.0,
        1.0,
        float(poids_reference.get("Perf_1_ semaine", 0.25)),
        0.05
    )

    poids_mois = st.sidebar.slider(
        "Performance 1 mois",
        0.0,
        1.0,
        float(poids_reference.get("Perf_1_ mois", 0.00)),
        0.05
    )

    total = (
        poids_an
        + poids_frais
        + poids_ytd
        + poids_sem
        + poids_mois
    )

    if total == 0:
        st.error("La somme des poids doit être supérieure à 0.")
        st.stop()

    score_df = df.copy()

    score_df["AN_norm"] = (
        score_df["AN"] - score_df["AN"].min()
    ) / (
        score_df["AN"].max() - score_df["AN"].min()
    )

    score_df["Frais_norm"] = (
        score_df["Frais de gestion"].max()
        - score_df["Frais de gestion"]
    ) / (
        score_df["Frais de gestion"].max()
        - score_df["Frais de gestion"].min()
    )

    score_df["YTD_norm"] = (
        score_df["Perf_YTD"]
        - score_df["Perf_YTD"].min()
    ) / (
        score_df["Perf_YTD"].max()
        - score_df["Perf_YTD"].min()
    )

    score_df["Semaine_norm"] = (
        score_df["Perf_1_ semaine"]
        - score_df["Perf_1_ semaine"].min()
    ) / (
        score_df["Perf_1_ semaine"].max()
        - score_df["Perf_1_ semaine"].min()
    )

    score_df["Mois_norm"] = (
        score_df["Perf_1_ mois"]
        - score_df["Perf_1_ mois"].min()
    ) / (
        score_df["Perf_1_ mois"].max()
        - score_df["Perf_1_ mois"].min()
    )

    score_df["Score"] = (

        score_df["AN_norm"] * poids_an

        + score_df["Frais_norm"] * poids_frais

        + score_df["YTD_norm"] * poids_ytd

        + score_df["Semaine_norm"] * poids_sem

        + score_df["Mois_norm"] * poids_mois

    ) / total

    score_df["Rang"] = score_df["Score"].rank(
        ascending=False,
        method="dense"
    )

    score_df = score_df.sort_values(
        "Score",
        ascending=False
    )

    score_df["Rang"] = range(
        1,
        len(score_df) + 1
    )

    st.subheader("🏆 Classement")

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

    st.subheader("📊 Top 10")

    fig_bar = px.bar(
        score_df.head(10),
        x="OPCVM",
        y="Score",
        color="Score",
        text="Score"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    st.subheader("🕸 Radar OPCVM")

    selection = st.multiselect(
        "Choisir des OPCVM",
        score_df["OPCVM"].tolist(),
        default=score_df.head(3)["OPCVM"].tolist()
    )

    if selection:

        radar_df = score_df[
            score_df["OPCVM"].isin(selection)
        ]

        fig_radar = go.Figure()

        categories = [
            "Taille",
            "Frais",
            "YTD",
            "Semaine",
            "Mois"
        ]

        for _, row in radar_df.iterrows():

            valeurs = [

                row["AN_norm"],
                row["Frais_norm"],
                row["YTD_norm"],
                row["Semaine_norm"],
                row["Mois_norm"]

            ]

            valeurs.append(valeurs[0])

            fig_radar.add_trace(
                go.Scatterpolar(
                    r=valeurs,
                    theta=categories + ["Taille"],
                    fill="toself",
                    name=row["OPCVM"]
                )
            )

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            height=700
        )

        st.plotly_chart(
            fig_radar,
            use_container_width=True
        )

    st.subheader("🔥 Heatmap Interactive")

    heatmap_df = (
        score_df
        .head(20)
        .set_index("OPCVM")
        [
            [
                "AN_norm",
                "Frais_norm",
                "YTD_norm",
                "Semaine_norm",
                "Mois_norm",
                "Score"
            ]
        ]
    )

    fig_heat = px.imshow(
        heatmap_df,
        text_auto=".2f",
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )

    fig_heat.update_layout(
        height=700,
        xaxis_title="Critères",
        yaxis_title="OPCVM"
    )

    st.plotly_chart(
        fig_heat,
        use_container_width=True
    )

    st.subheader("📥 Export")

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        score_df.to_excel(
            writer,
            sheet_name="Classement",
            index=False
        )

    st.download_button(
        label="Télécharger le classement Excel",
        data=output.getvalue(),
        file_name="Classement_OPCVM.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:

    st.info(
        "Chargez le fichier Excel OPCVM pour commencer."
    )
