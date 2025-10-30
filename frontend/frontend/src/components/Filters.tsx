import { useState } from "react";
import type { Product } from "../types";

interface FiltersProps {
  products: Product[];
  setFiltered: (products: Product[]) => void;
  fetchProducts: (params?: any) => Promise<void>; // <-- ajouter ici
}

export default function Filters({ products, setFiltered, fetchProducts }: FiltersProps) {
  const [searchText, setSearchText] = useState("");
  const [nutriScore, setNutriScore] = useState("");

  const handleFilter = () => {
    const params: any = {};
    if (searchText) params.q = searchText;
    if (nutriScore) params.nutri = nutriScore;
    fetchProducts(params);
  };

  return (
    <div className="mb-4 flex gap-4">
      <input
        type="text"
        placeholder="Nom, marque ou catégorie..."
        value={searchText}
        onChange={e => setSearchText(e.target.value)}
        className="border p-2 rounded"
      />
      <select
        value={nutriScore}
        onChange={e => setNutriScore(e.target.value)}
        className="border p-2 rounded"
      >
        <option value="">Tous NutriScore</option>
        <option value="A">A</option>
        <option value="B">B</option>
        <option value="C">C</option>
        <option value="D">D</option>
        <option value="E">E</option>
      </select>
      <button onClick={handleFilter} className="bg-blue-500 text-white px-4 py-2 rounded">
        Filtrer
      </button>
    </div>
  );
}
