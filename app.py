import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import rankdata
from io import BytesIO

st.set_page_config(
    page_title="OPCVM Scoring",
    layout="wide"
)

st.title("📊 OPCVM Ranking Dashboard")

uploaded_file = st.file_uploader(
    "Charger le fichier OPCVM",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.sidebar.header("Paramètres")

    poids_taille = st.sidebar.slider(
        "Poids Taille",
        0.0,
        1.0,
        0.15
    )

    poids_frais = st.sidebar.slider(
        "Poids Frais",
        0.0,
        1.0,
        0.20
    )

    poids_perf1a = st.sidebar.slider(
        "Poids Performance 1 an",
        0.0,
        1.0,
        0.20
    )

    poids_perf3a = st.sidebar.slider(
        "Poids Performance 3 ans",
        0.0,
        1.0,
        0.20
    )

    poids_perf5a = st.sidebar.slider(
        "Poids Performance 5 ans",
        0.0,
        1.0,
        0.25
    )

    total = (
        poids_taille
        + poids_frais
        + poids_perf1a
        + poids_perf3a
        + poids_perf5a
    )

    if total == 0:
        st.error("Le total des poids doit être supérieur à zéro")
        st.stop()

    poids_taille /= total
    poids_frais /= total
    poids_perf1a /= total
    poids_perf3a /= total
    poids_perf5a /= total

    colonnes = [
        "OPCVM",
        "AN",
        "Frais de gestion",
        "Perf_1_an",
        "Perf_3_an",
        "Perf_5_an"
    ]

    data = df[colonnes].copy()

    data = data.dropna()

    data["Score_Taille"] = (
        rankdata(data["AN"])
        / len(data)
    )

    data["Score_Frais"] = 1 - (
        rankdata(data["Frais de gestion"])
        / len(data)
    )

    data["Score_1A"] = (
        rankdata(data["Perf_1_an"])
        / len(data)
    )

    data["Score_3A"] = (
        rankdata(data["Perf_3_an"])
        / len(data)
    )

    data["Score_5A"] = (
        rankdata(data["Perf_5_an"])
        / len(data)
    )

    data["Score_Global"] = (

        data["Score_Taille"] * poids_taille

        + data["Score_Frais"] * poids_frais

        + data["Score_1A"] * poids_perf1a

        + data["Score_3A"] * poids_perf3a

        + data["Score_5A"] * poids_perf5a
    )

    data = data.sort_values(
        "Score_Global",
        ascending=False
    )

    data["Rang"] = range(
        1,
        len(data) + 1
    )

    st.subheader("🏆 Top 10")

    st.dataframe(
        data.head(10),
        use_container_width=True
    )

    st.subheader("Classement complet")

    st.dataframe(
        data,
        use_container_width=True
    )

    st.subheader("Score Global")

    st.bar_chart(
        data.set_index("OPCVM")["Score_Global"].head(20)
    )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter"
    ) as writer:

        data.to_excel(
            writer,
            index=False,
            sheet_name="Classement"
        )

    st.download_button(
        label="📥 Télécharger le classement",
        data=output.getvalue(),
        file_name="Classement_OPCVM.xlsx",
        mime="application/vnd.ms-excel"
    )

else:

    st.info(
        "Chargez le fichier Excel OPCVM pour démarrer."
    )
