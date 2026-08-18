# OPCVM Scoring Dashboard

Application Streamlit permettant d'analyser et classer les OPCVM selon une approche multicritères.

## Fonctionnalités

- Chargement dynamique des données OPCVM
- Paramétrage des poids des critères
- Calcul automatique des scores
- Classement des fonds
- Dashboard interactif
- Export Excel du classement

## Critères analysés

- Taille (Actif Net)
- Frais de gestion
- Performance 1 an
- Performance 3 ans
- Performance 5 ans

## Méthodologie

Chaque critère est normalisé via une méthode percentile.

Le score global est calculé :

Score =

(Taille × Poids_Taille)

+ (Frais × Poids_Frais)

+ (Perf1A × Poids_1A)

+ (Perf3A × Poids_3A)

+ (Perf5A × Poids_5A)

Les frais étant un critère à minimiser, leur score est inversé.

## Installation locale

```bash
git clone https://github.com/votrecompte/opcvm-scoring.git

cd opcvm-scoring

pip install -r requirements.txt

streamlit run app.py
```

## Déploiement Streamlit Cloud

1. Déposer le code sur GitHub
2. Aller sur :

https://share.streamlit.io

3. Connecter le dépôt GitHub
4. Choisir :

```text
app.py
```

5. Deploy

## Auteur

Fouad Boukhnif
