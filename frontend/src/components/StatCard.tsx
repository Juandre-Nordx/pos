type StatCardProps = {
  label: string;
  value: string;
  hint?: string;
  icon: string;
  tone?: 'blue' | 'green' | 'amber' | 'red';
};

const tones = {
  blue: 'bg-blue-50 text-blue-700 ring-blue-100',
  green: 'bg-emerald-50 text-emerald-700 ring-emerald-100',
  amber: 'bg-amber-50 text-amber-700 ring-amber-100',
  red: 'bg-red-50 text-red-700 ring-red-100',
};

export function StatCard({ label, value, hint, icon, tone = 'blue' }: StatCardProps) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <h3 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">{value}</h3>
        </div>
        <div className={`rounded-2xl p-3 ring-1 ${tones[tone]}`}>
          <span aria-hidden="true">{icon}</span>
        </div>
      </div>
      {hint ? <p className="mt-4 text-sm text-slate-500">{hint}</p> : null}
    </article>
  );
}
