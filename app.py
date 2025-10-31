# app.py
import os, time, random, logging
import pandas as pd
import matplotlib.pyplot as plt
from utiles import Scraper, Repository, Cleaner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    # -------- Config --------
    categories = ["waters", "biscuits", "chocolates", "cookiesbreakfast-cereals", "yogurts"]
    max_pages_per_category = 2
    barcode_limit_total = 120

    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    mongo_db  = os.environ.get("MONGO_DB", "food_db")

    scraper = Scraper()
    repo = Repository(uri=mongo_uri, db_name=mongo_db, collection="produits")
    cleaner = Cleaner()

    # -------- 1) Discover barcodes --------
    logging.info("Découverte des codes-barres…")
    barcodes = scraper.discover_barcodes(categories, max_pages=max_pages_per_category, limit=barcode_limit_total)
    logging.info(f"{len(barcodes)} codes-barres découverts.")

    # -------- 2) Fetch + parse --------
    inserted = 0
    for i, code in enumerate(barcodes, 1):
        try:
            data = scraper.fetch_product(code)
            data = cleaner.clean(data)
            if not data:
                logging.warning(f"[{i}/{len(barcodes)}] {code}: aucune donnée – skip.")
                continue
            repo.upsert(data, key="barcode")
            inserted += 1
            logging.info(f"[{i}/{len(barcodes)}] {code}: OK")
        except Exception as e:
            logging.exception(f"[{i}/{len(barcodes)}] {code}: {e}")
        finally:
            time.sleep(random.uniform(0.4, 0.9))
    logging.info(f"Insertion terminée. {inserted} produits traités.")

    # -------- 3) Export + charts --------
    docs = repo.all()
    df = pd.DataFrame(docs)
    if df.empty:
        logging.warning("Base vide — pas d’export/graphes.")
        repo.close()
        return
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    df.to_excel("produits_openfoodfacts.xlsx", index=False)
    logging.info("Fichier Excel généré: produits_openfoodfacts.xlsx")

    # Graph NutriScore
    if "nutriscore" in df.columns:
        s = df["nutriscore"].fillna("").replace("", pd.NA).dropna()
        if not s.empty:
            g = s.value_counts().sort_index().reset_index()
            g.columns = ["nutriscore", "count"]
            ax = g.plot(kind="bar", x="nutriscore", y="count", legend=False, title="Répartition du NutriScore")
            ax.set_xlabel("NutriScore"); ax.set_ylabel("Nombre de produits"); ax.figure.tight_layout()
            ax.figure.savefig("nutriscore_distribution.png")
            logging.info("Graphique généré: nutriscore_distribution.png")

    # Graph catégories
    if "categorie" in df.columns:
        cs = df["categorie"].fillna("").replace("", pd.NA).dropna()
        if not cs.empty:
            top10 = cs.str.split(", ").explode().value_counts().head(10)
            if not top10.empty:
                ax2 = top10.plot(kind="bar", title="Top 10 catégories")
                ax2.set_ylabel("Nombre de produits"); ax2.figure.tight_layout()
                ax2.figure.savefig("top10_categories.png")
                logging.info("Graphique généré: top10_categories.png")

    repo.close()
    logging.info("Pipeline terminé avec succès.")

if __name__ == "__main__":
    main()