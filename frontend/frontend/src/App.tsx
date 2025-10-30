import { useEffect, useState } from "react";
import axios from "axios";
import ProductsTable from "./components/ProductsTable";
import Filters from "./components/Filters";
import type { Product } from "./types";

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [filtered, setFiltered] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 10;

  const fetchProducts = async (params: Record<string, any> = {}) => {
    try {
      const res = await axios.get("http://localhost:5000/api/products", {
        params: { page, limit, ...params },
      });
      setProducts(res.data.data);
      setFiltered(res.data.data);
      setTotalPages(Math.ceil(res.data.total / limit));
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="max-w-6xl mx-auto">

        {/* ✅ BEAUTIFUL CENTERED HEADER */}
        <header className="mb-8">
          <h1 className="page-title">
            OpenFoodFacts Products
          </h1>
          <p className="page-subtitle">
            Explore nutrition at a glance — filter, scan, and compare.
          </p>
        </header>

        {/* ✅ FILTERS CARD */}
        <section className="mb-4 rounded-xl border border-sky-100 bg-white/80 backdrop-blur-md shadow p-4">
          <Filters
            products={products}
            setFiltered={setFiltered}
            fetchProducts={fetchProducts}
          />
        </section>

        {/* ✅ TABLE CARD */}
        <section className="rounded-xl border border-sky-100 bg-white/90 backdrop-blur-md shadow">
          <ProductsTable
            products={filtered}
            page={page}
            setPage={setPage}
            totalPages={totalPages}
          />
        </section>

      </div>
    </div>
  );
}
