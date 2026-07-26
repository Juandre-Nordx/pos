import type { ReactNode } from 'react';

type Column<T> = {
  header: string;
  render: (row: T) => ReactNode;
};

type DataTableProps<T> = {
  title: string;
  description?: string;
  rows: T[];
  columns: Column<T>[];
  getKey: (row: T) => string;
  emptyText?: string;
};

export function DataTable<T>({ title, description, rows, columns, getKey, emptyText = 'No records found.' }: DataTableProps<T>) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 p-5">
        <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
        {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>{columns.map((column) => <th className="px-5 py-3 font-semibold" key={column.header}>{column.header}</th>)}</tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.length ? rows.map((row) => (
              <tr className="hover:bg-slate-50" key={getKey(row)}>
                {columns.map((column) => <td className="px-5 py-4 text-slate-700" key={column.header}>{column.render(row)}</td>)}
              </tr>
            )) : (
              <tr><td className="px-5 py-8 text-center text-slate-500" colSpan={columns.length}>{emptyText}</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
