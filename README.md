# OpenFoodFacts Scraper

Projet Python pour collecter, nettoyer, stocker et analyser des données produits depuis [OpenFoodFacts](https://world.openfoodfacts.org/).

---

## Fonctionnalités

* Scraping des données produit à partir de **50 codes-barres OpenFoodFacts**
* Nettoyage et transformation des données
* Stockage dans **MongoDB**
* Export des données en **Excel** (`produits_openfoodfacts.xlsx`)
* Analyse simple et graphiques :

  * Répartition des produits par **NutriScore**
  * Top 10 des **catégories** de produits
* Gestion des exceptions pour HTTP, MongoDB, export Excel et génération de graphiques
* Pipeline complet organisé dans `app.py`
* Classes modulaires dans `utiles.py` (`Scraper`, `Cleaner`, `DBManager`)

---

## Structure du projet

```
openfoodfacts_project/
│
├── app.py                 # Pipeline principal : scraping → nettoyage → MongoDB → Excel → graphiques
├── utiles.py              # Classes : Scraper, Cleaner, DBManager
├── requirements.txt       # Librairies Python nécessaires
├── README.md              # Ce fichier
└── .gitignore             # Exclut fichiers volumineux et temporaires (Excel, PNG, venv, etc.)
```

---

## Prérequis

* Python 3.x
* MongoDB (local ou MongoDB Atlas)
* Librairies Python :

```bash
pip install -r requirements.txt
```

---

## Configuration MongoDB

* **Local** : MongoDB doit être en cours d’exécution (`mongodb://localhost:27017/`)
* **Atlas** : remplacer l’URI dans `DBManager` par votre URI MongoDB Atlas :

```python
db = DBManager(uri="mongodb+srv://<user>:<password>@cluster0.mongodb.net/food_db")
```

---

## Utilisation

1. Cloner le dépôt :

```bash
git clone https://github.com/ChakrounFerdaouss/openfoodfacts_project.git
cd openfoodfacts_project
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Lancer le pipeline :

```bash
python app.py
```

4. Résultat attendu :

   * Base MongoDB mise à jour avec les produits
   * Fichier Excel généré : `produits_openfoodfacts.xlsx`
   * Graphiques générés : `nutriscore_distribution.png` et `top10_categories.png`

---

## Notes

* Le projet respecte **l’éthique du scraping** : petits volumes, gestion des exceptions, pas de surcharge serveur.
* `.gitignore` exclut : fichiers Excel, PNG, bases de données locales, et dossiers IDE/venv.
* Peut être adapté facilement pour plus de produits ou d’autres analyses.

---

## Site web

Lancer Backend : 

```bash
cd backend
npm install
npm run dev
```

Lancer Frontend : 

```bash
cd frontend/frontend
npm install
npm run dev
```