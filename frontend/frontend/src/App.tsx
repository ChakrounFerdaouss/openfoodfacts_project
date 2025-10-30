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

  const fetchProducts = async (params = {}) => {
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
  }, [page]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">OpenFoodFacts Products</h1>
      <Filters products={products} setFiltered={setFiltered} fetchProducts={fetchProducts} />
      <ProductsTable
        products={filtered}
        page={page}
        setPage={setPage}
        totalPages={totalPages}
      />
    </div>
  );
}
