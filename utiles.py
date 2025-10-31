# utiles.py
import time, random, re, logging
from typing import Iterable, List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError

class Scraper:
    def __init__(self, base="https://world.openfoodfacts.org", timeout=12, retries=3):
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
            "Accept-Language": "en,fr;q=0.9",
        }

    # -------- HTTP --------
    def _get(self, url: str) -> Optional[requests.Response]:
        last = None
        for attempt in range(self.retries + 1):
            try:
                r = requests.get(url, headers=self.headers, timeout=self.timeout)
                r.raise_for_status()
                time.sleep(random.uniform(0.5, 1.1))
                return r
            except Exception as e:
                last = e
                time.sleep(0.6 * (attempt + 1))
        raise last

    # -------- Discovery (3 strategies) --------
    def discover_barcodes(self, categories: Iterable[str], max_pages: int = 1, limit: Optional[int] = None) -> List[str]:
        found: List[str] = []
        seen = set()

        def try_page(url: str) -> int:
            """Return number of new barcodes found on this page."""
            try:
                resp = self._get(url)
                soup = BeautifulSoup(resp.content, "html.parser")
                anchors = soup.select('a[href^="/product/"], a[href*="/product/"]')
                if not anchors:
                    anchors = soup.find_all(href=re.compile(r"/product/\d{8,14}"))
                new = 0
                for a in anchors:
                    m = re.search(r"/product/(\d{8,14})", a.get("href", ""))
                    if m:
                        code = m.group(1)
                        if code not in seen:
                            seen.add(code); found.append(code); new += 1
                            if limit and len(found) >= limit:
                                return new
                if new == 0:  # last-resort regex over whole HTML
                    for m in re.finditer(r"/product/(\d{8,14})", resp.text):
                        code = m.group(1)
                        if code not in seen:
                            seen.add(code); found.append(code); new += 1
                            if limit and len(found) >= limit:
                                return new
                return new
            except Exception as e:
                logging.warning(f"Découverte: {e} @ {url}")
                return 0

        for raw in categories:
            slug = raw.split(":", 1)[-1].strip()  # accept 'en:chocolates' or 'chocolates'
            for page in range(1, max_pages + 1):
                # Strategy A: /category/<slug>[?page=N]/N
                candidates = [f"{self.base}/category/{slug}"]
                if page > 1:
                    candidates += [f"{self.base}/category/{slug}?page={page}",
                                   f"{self.base}/category/{slug}/{page}"]
                # Strategy B: language taxonomy /category/en:<slug>
                if page == 1:
                    candidates.append(f"{self.base}/category/en:{slug}")
                else:
                    candidates += [f"{self.base}/category/en:{slug}?page={page}",
                                   f"{self.base}/category/en:{slug}/{page}"]
                # Strategy C: HTML search page (stable fallback)
                q = slug.replace("-", "+")
                if page == 1:
                    candidates.append(f"{self.base}/cgi/search.pl?search_terms={q}&search_simple=1&action=process")
                else:
                    candidates.append(f"{self.base}/cgi/search.pl?search_terms={q}&page={page}&search_simple=1&action=process")

                before = len(found)
                for url in candidates:
                    logging.info(f"Découverte → {url}")
                    added = try_page(url)
                    if limit and len(found) >= limit:
                        logging.info(f"Limite atteinte ({limit}).")
                        return found
                    if added > 0:
                        break  # go to next page after a successful variant

                logging.info(f"{slug} p{page}: +{len(found)-before} (total {len(found)})")

        return found

    # -------- Product parsing --------
    def fetch_product(self, barcode: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base}/product/{barcode}"
        try:
            resp = self._get(url)
            txt = resp.text.lower()
            if "product not found" in txt or "we couldn't find this product" in txt:
                return None
            soup = BeautifulSoup(resp.content, "html.parser")

            name = self._first_text(soup, ["#field_product_name_value",
                                           "h1[itemprop='name']", "h1#product_name", "h1"])
            brand = self._first_text(soup, ["#field_brands_value",
                                            "a[href*='/brand/']", "[itemprop='brand']"])
            categories = self._list_text(soup, ["#field_categories_value a",
                                                "a[href*='/category/']", "a[property='food:category']"])
            nutri = ""
            img = soup.select_one("img[class*='nutri'], img[src*='nutriscore'], img[alt*='Nutri-Score']")
            if img:
                bucket = " ".join([img.get("alt") or "", img.get("title") or "", img.get("src") or ""])
                m = re.search(r"[Nn]utri[- ]?[Ss]core[^A-E]*([A-E])", bucket) or re.search(r"nutri(?:score)?[-_/]?([a-e])", bucket, re.I)
                if m: nutri = m.group(1).upper()
            labels = self._list_text(soup, ["#field_labels_value a", "a[href*='/label/']", "div.labels a"])

            return {
                "barcode": barcode,
                "nom": name or "",
                "marque": brand or "",
                "categorie": ", ".join(categories) if categories else "",
                "nutriscore": nutri or "",
                "labels": ", ".join(labels) if labels else "",
                "source_url": url,
            }
        except Exception as e:
            logging.warning(f"Produit {barcode}: {e}")
            return None

    # -------- Helpers --------
    @staticmethod
    def _first_text(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                t = el.get_text(strip=True)
                if t: return t
        return None

    @staticmethod
    def _list_text(soup: BeautifulSoup, selectors: List[str]) -> List[str]:
        for sel in selectors:
            els = soup.select(sel)
            if els:
                vals = [e.get_text(strip=True) for e in els if e.get_text(strip=True)]
                vals = list(dict.fromkeys(vals))
                if vals: return vals
        return []

class Cleaner:
    KEYS = ["barcode", "nom", "marque", "categorie", "nutriscore", "labels", "source_url"]
    def clean(self, d: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not d: return None
        for k in self.KEYS:
            d.setdefault(k, ""); d[k] = d[k] or ""
        return d

class Repository:
    def __init__(self, uri: str, db_name: str, collection: str = "produits"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.col = self.db[collection]
        self.col.create_index([("barcode", ASCENDING)], unique=True)

    def upsert(self, doc: Dict[str, Any], key: str = "barcode") -> None:
        if not doc or not doc.get(key): return
        try:
            self.col.update_one({key: doc[key]}, {"$set": doc}, upsert=True)
        except PyMongoError as e:
            logging.warning(f"Mongo upsert error {doc.get(key)}: {e}")

    def all(self):
        try:
            return list(self.col.find())
        except PyMongoError as e:
            logging.warning(f"Mongo read error: {e}")
            return []

    def close(self):
        try: self.client.close()
        except Exception: pass
        