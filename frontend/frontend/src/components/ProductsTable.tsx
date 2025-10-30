import type { Product } from "../types";
import React from "react";

interface ProductsTableProps {
  products: Product[];
  page: number;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  totalPages: number;
}

function NutriBadge({ grade }: { grade: string }) {
  const g = (grade || "").toUpperCase();
  const map: Record<string, string> = {
    A: "bg-emerald-100 text-emerald-800 border-emerald-300",
    B: "bg-lime-100 text-lime-800 border-lime-300",
    C: "bg-amber-100 text-amber-800 border-amber-300",
    D: "bg-orange-100 text-orange-800 border-orange-300",
    E: "bg-rose-100 text-rose-800 border-rose-300",
  };
  const cls = map[g] || "bg-slate-100 text-slate-700 border-slate-300";
  return (
    <span
      className={`inline-flex min-w-7 justify-center rounded-md border px-2 py-0.5 text-sm font-semibold ${cls}`}
      title={g || "-"}
    >
      {g || "-"}
    </span>
  );
}

export default function ProductsTable({
  products,
  page,
  setPage,
  totalPages,
}: ProductsTableProps) {
  const handlePrev = () => setPage((p: number) => Math.max(1, p - 1));
  const handleNext = () => setPage((p: number) => Math.min(totalPages, p + 1));

  return (
    // ✅ FIX: removed the padding
    <div className="p-0 mt-2">

      <div className="table-card overflow-x-auto">
        <table className="w-full border-collapse">
          <thead className="sticky top-0 z-10 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
            <tr className="text-slate-600">
              <th className="p-3 sm:p-4 text-left font-semibold border-b border-slate-200">Nom</th>
              <th className="p-3 sm:p-4 text-left font-semibold border-b border-slate-200">Marque</th>
              <th className="p-3 sm:p-4 text-left font-semibold border-b border-slate-200">Catégorie</th>
              <th className="p-3 sm:p-4 text-left font-semibold border-b border-slate-200">NutriScore</th>
              <th className="p-3 sm:p-4 text-left font-semibold border-b border-slate-200">Labels</th>
            </tr>
          </thead>

          <tbody>
            {products.map((p: Product, i: number) => (
              <tr
                key={p.barcode}
                className={`transition-colors ${
                  i % 2 === 0 ? "bg-white" : "bg-sky-50/40"
                } hover:bg-sky-100/40`}
              >
                <td className="p-3 sm:p-4 border-b border-slate-200 text-slate-900">
                  <span className="block max-w-[22rem] truncate" title={p.nom}>
                    {p.nom}
                  </span>
                </td>

                <td className="p-3 sm:p-4 border-b border-slate-200 text-slate-700">
                  <span className="block max-w-[12rem] truncate" title={p.marque}>
                    {p.marque}
                  </span>
                </td>

                <td className="p-3 sm:p-4 border-b border-slate-200 text-slate-700">
                  <span className="block max-w-[40rem] truncate" title={p.categorie}>
                    {p.categorie}
                  </span>
                </td>

                <td className="p-3 sm:p-4 border-b border-slate-200">
                  <NutriBadge grade={p.nutriscore} />
                </td>

                <td className="p-3 sm:p-4 border-b border-slate-200">
                  <div className="flex max-w-[42rem] flex-wrap gap-1.5">
                    {(p.labels || "")
                      .split(/[,|]/)
                      .map((l) => l.trim())
                      .filter(Boolean)
                      .map((l, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center rounded-full border border-slate-200 bg-white/90 px-2 py-0.5 text-[12px] text-slate-700"
                          title={l}
                        >
                          {l}
                        </span>
                      ))}
                  </div>
                </td>
              </tr>
            ))}

            {products.length === 0 && (
              <tr>
                <td colSpan={5} className="p-8 text-center text-slate-500 bg-white">
                  Aucun produit trouvé.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="text-sm text-slate-600">
          Page {page} / {totalPages}
        </div>
        <div className="inline-flex items-center gap-2">
          <button
            onClick={handlePrev}
            disabled={page === 1}
            className="rounded-xl border border-sky-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm transition hover:shadow disabled:opacity-50"
          >
            Précédent
          </button>
          <button
            onClick={handleNext}
            disabled={page === totalPages}
            className="rounded-xl border border-sky-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm transition hover:shadow disabled:opacity-50"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>
  );
}
