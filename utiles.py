import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

class Scraper:
    """Scraper HTML des produits OpenFoodFacts"""

    def __init__(self, base_url="https://world.openfoodfacts.org/product/"):
        self.base_url = base_url

    def fetch_product(self, barcode):
        try:
            url = f"{self.base_url}{barcode}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            nom = soup.find("h1", {"property": "food:name"})
            nom = nom.text.strip() if nom else ""

            marque = soup.find("a", {"property": "brand"})
            marque = marque.text.strip() if marque else ""

            categorie_tags = soup.find_all("a", {"property": "food:category"})
            categorie = ", ".join([c.text.strip() for c in categorie_tags]) if categorie_tags else ""

            nutriscore = soup.find("img", {"class": "nutriscore"})
            nutriscore = nutriscore["alt"].strip() if nutriscore else ""

            labels_tag = soup.find("div", {"class": "labels"})
            labels = labels_tag.text.strip() if labels_tag else ""

            return {
                "barcode": barcode,
                "nom": nom,
                "marque": marque,
                "categorie": categorie,
                "nutriscore": nutriscore,
                "labels": labels
            }

        except requests.exceptions.Timeout:
            print(f"Timeout pour le produit {barcode}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erreur HTTP pour {barcode}: {e}")
            return None

class Cleaner:
    """Nettoyage et transformation des données"""

    def clean(self, product_data):
        if product_data is None:
            return None
        for key in ["barcode", "nom", "marque", "categorie", "nutriscore", "labels"]:
            if key not in product_data or product_data[key] is None:
                product_data[key] = ""
        return product_data

class DBManager:
    """Gestion de la BDD MongoDB"""

    def __init__(self, uri="mongodb://localhost:27017/", db_name="food_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["produits"]

    def insert_product(self, product):
        if product is None:
            return
        try:
            self.collection.update_one(
                {"barcode": product["barcode"]},
                {"$set": product},
                upsert=True
            )
        except Exception as e:
            print(f"Erreur insertion produit {product['barcode']}: {e}")

    def get_all_products(self):
        try:
            return list(self.collection.find())
        except Exception as e:
            print(f"Erreur récupération produits : {e}")
            return []

    def close(self):
        self.client.close()
