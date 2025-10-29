# OpenFoodFacts Project - BeautifulSoup

## Description
Projet de collecte et traitement de données alimentaires depuis OpenFoodFacts via scraping HTML.  
Pipeline complet : collecte → nettoyage → stockage SQLite → analyse simple.

## Fonctionnalités
- Scraping HTML des pages produits (nom, marque, catégories, NutriScore, labels)
- Nettoyage des données
- Stockage dans SQLite (`produits`)
- Analyse simple :
  - Répartition des NutriScores
  - Top 10 des catégories les plus fréquentes
- Gestion des exceptions (timeout, HTTP, produit non trouvé)
- Pipeline structuré avec classes : `Scraper`, `Cleaner`, `DBManager`
- Commentaires et docstrings pour GitHub

## Installation
```bash
git clone <repo_url>
cd meteo_project
pip install -r requirements.txt
