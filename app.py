from utiles import Scraper, Cleaner, DBManager
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 50 codes-barres aléatoires d'exemple
    barcodes = [
        "3017620425035","8000500037568","3274080005003","3017620422004","3017620425110",
        "5410188030197","3229820000733","3229820000641","3274080011472","7622210449283",
        "7613034627344","3057640077777","3596710950008","3229820000734","3263850091190",
        "3274080010006","7613034627269","3017620425059","5410188030012","3229820000056",
        "3229820000032","3229820000063","3274080011473","7622210449290","7613034627351",
        "3057640077778","3596710950009","3229820000735","3263850091191","3274080010007",
        "7613034627270","3017620425060","5410188030013","3229820000057","3229820000033",
        "3229820000064","3274080011474","7622210449291","7613034627352","3057640077779",
        "3596710950010","3229820000736","3263850091192","3274080010008","7613034627271",
        "3017620425061","5410188030014","3229820000058","3229820000034","3229820000065"
    ]

    scraper = Scraper()
    cleaner = Cleaner()
    db = DBManager()  # MongoDB

    for code in barcodes:
        try:
            raw_data = scraper.fetch_product(code)
            cleaned_data = cleaner.clean(raw_data)
            db.insert_product(cleaned_data)
            print(f"Produit {code} inséré dans MongoDB")
        except Exception as e:
            print(f"Erreur pour le produit {code}: {e}")

    # --- Export Excel ---
    try:
        products = db.get_all_products()
        df = pd.DataFrame(products)
        if "_id" in df.columns:
            df.drop("_id", axis=1, inplace=True)
        df.to_excel("produits_openfoodfacts.xlsx", index=False)
        print("Fichier Excel généré : produits_openfoodfacts.xlsx")
    except Exception as e:
        print(f"Erreur export Excel : {e}")

    # --- Analyse simple et graphiques ---
    try:
        df_nutri = df.groupby("nutriscore").size().reset_index(name="count")
        df_nutri.plot(kind="bar", x="nutriscore", y="count", legend=False, title="Répartition NutriScore")
        plt.xlabel("NutriScore")
        plt.ylabel("Nombre de produits")
        plt.savefig("nutriscore_distribution.png")
        print("Graphique NutriScore généré : nutriscore_distribution.png")

        df_cat = df["categorie"].value_counts().head(10)
        df_cat.plot(kind="bar", title="Top 10 catégories")
        plt.ylabel("Nombre de produits")
        plt.savefig("top10_categories.png")
        print("Graphique catégories généré : top10_categories.png")

        plt.show()
    except Exception as e:
        print(f"Erreur analyse ou graphique : {e}")

    db.close()
    print("Pipeline terminé avec succès!")

if __name__ == "__main__":
    main()
