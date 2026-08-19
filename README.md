# OPCVM Scoring Dashboard

Application Streamlit permettant d'analyser et de classer les OPCVM selon une approche multicritères dynamique.

---

## Fonctionnalités

✅ Chargement Excel

✅ Paramétrage dynamique des poids

✅ Classement des OPCVM

✅ Radar Chart

✅ Heatmap Interactive

✅ Top 10

✅ Export Excel

✅ Dashboard professionnel

---

## Critères

- Actif Net (AN)
- Frais de gestion
- Performance YTD
- Performance 1 semaine
- Performance 1 mois

---

## Méthodologie

Les données sont normalisées entre 0 et 1.

### Critères positifs

- AN
- Perf YTD
- Perf 1 semaine
- Perf 1 mois

### Critère négatif

- Frais de gestion

La normalisation est inversée pour les frais :

Score_Frais =
(Max-Frais)/(Max-Min)

---

## Formule

Score =

(AN_norm × Poids_AN)

+(Frais_norm × Poids_Frais)

+(YTD_norm × Poids_YTD)

+(Semaine_norm × Poids_Semaine)

+(Mois_norm × Poids_Mois)

---

## Installation

```bash
git clone https://github.com/votrecompte/opcvm-scoring.git

cd opcvm-scoring

pip install -r requirements.txt
```

## Exécution

```bash
streamlit run app.py
```

---

## Déploiement Streamlit Cloud

1. Déposer les fichiers sur GitHub

2. Aller sur :

https://share.streamlit.io

3. Choisir :

```text
Repository : opcvm-scoring

Branch : main

Main file : app.py
```

4. Deploy

---

## Auteur

Fouad BOUKHNIF

Chef de Division
