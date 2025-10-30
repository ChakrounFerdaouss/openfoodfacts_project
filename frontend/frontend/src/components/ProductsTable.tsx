import type { Product } from "../types";
import React from "react";

interface ProductsTableProps {
  products: Product[];
  page: number;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  totalPages: number;
}

export default function ProductsTable({ products, page, setPage, totalPages }: ProductsTableProps) {
  // Pagination boutons
  const handlePrev = () => setPage((p: number) => Math.max(1, p - 1));
  const handleNext = () => setPage((p: number) => Math.min(totalPages, p + 1));

  return (
    <div>
      <table className="table-auto border-collapse border border-gray-300 w-full mb-2">
        <thead>
          <tr>
            <th className="border p-2">Nom</th>
            <th className="border p-2">Marque</th>
            <th className="border p-2">Catégorie</th>
            <th className="border p-2">NutriScore</th>
            <th className="border p-2">Labels</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p: Product) => (
            <tr key={p.barcode}>
              <td className="border p-2">{p.nom}</td>
              <td className="border p-2">{p.marque}</td>
              <td className="border p-2">{p.categorie}</td>
              <td className="border p-2">{p.nutriscore}</td>
              <td className="border p-2">{p.labels}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex justify-between items-center">
        <button
          onClick={handlePrev}
          disabled={page === 1}
          className="border p-2 rounded disabled:opacity-50"
        >
          Précédent
        </button>
        <span>Page {page} / {totalPages}</span>
        <button
          onClick={handleNext}
          disabled={page === totalPages}
          className="border p-2 rounded disabled:opacity-50"
        >
          Suivant
        </button>
      </div>
    </div>
  );
}
