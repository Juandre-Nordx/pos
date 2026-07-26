import { useEffect, useMemo, useState } from 'react';
import { api, clearTokens, getStoredToken } from './api/client';
import { DataTable } from './components/DataTable';
import { StatCard } from './components/StatCard';
import { LoginPage } from './pages/LoginPage';
import type { Client, Dashboard, PPECompliance, PPEIssue, PPEItem, Product, User } from './types/api';
import './styles.css';

const currency = new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR' });

function money(value: string | number) {
  return currency.format(Number(value));
}

function App() {
  const [token, setToken] = useState(getStoredToken());
  const [user, setUser] = useState<User | null>(null);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [ppeCompliance, setPpeCompliance] = useState<PPECompliance | null>(null);
  const [ppeItems, setPpeItems] = useState<PPEItem[]>([]);
  const [ppeIssues, setPpeIssues] = useState<PPEIssue[]>([]);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    let active = true;
    setLoading(true);
    setError('');
    Promise.all([api.me(), api.dashboard(), api.clients(search), api.products(search), api.ppeCompliance(), api.ppeItems(), api.ppeIssues()])
      .then(([me, dash, clientRows, productRows, compliance, itemRows, issueRows]) => {
        if (!active) return;
        setUser(me);
        setDashboard(dash);
        setClients(clientRows);
        setProducts(productRows);
        setPpeCompliance(compliance);
        setPpeItems(itemRows);
        setPpeIssues(issueRows);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load dashboard'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [token, search]);

  const lowStockCount = useMemo(() => products.filter((product) => product.is_low_stock).length, [products]);

  if (!token) return <LoginPage onLogin={() => setToken(getStoredToken())} />;

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <aside className="fixed inset-y-0 left-0 hidden w-72 flex-col border-r border-slate-200 bg-slate-950 p-6 text-white lg:flex">
        <div className="flex items-center gap-3"><div className="rounded-2xl bg-blue-500 p-3"><span aria-hidden="true">🛡️</span></div><div><p className="text-xs uppercase tracking-[0.35em] text-blue-200">Nordx</p><h1 className="text-xl font-bold">POS ERP</h1></div></div>
        <nav className="mt-10 space-y-2 text-sm font-medium text-slate-300">
          {['Dashboard', 'Clients', 'Inventory', 'PPE Compliance'].map((item) => <a className="block rounded-2xl px-4 py-3 hover:bg-white/10" href={`#${item.toLowerCase().replaceAll(' ', '-')}`} key={item}>{item}</a>)}
        </nav>
        <button className="mt-auto flex items-center gap-2 rounded-2xl px-4 py-3 text-left text-sm text-slate-300 hover:bg-white/10" onClick={() => { clearTokens(); setToken(null); }}><span aria-hidden="true">↩</span> Sign out</button>
      </aside>
      <main className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/85 px-5 py-4 backdrop-blur lg:px-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div><p className="text-sm text-slate-500">Welcome back{user ? `, ${user.first_name}` : ''}</p><h2 className="text-2xl font-bold">Operations dashboard</h2></div>
            <label className="flex w-full max-w-md items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500"><span aria-hidden="true">🔎</span><input className="w-full outline-none" placeholder="Search clients and inventory…" value={search} onChange={(event) => setSearch(event.target.value)} /></label>
          </div>
        </header>
        <div className="space-y-8 p-5 lg:p-8">
          {error ? <div className="rounded-3xl border border-red-200 bg-red-50 p-5 text-red-700">{error}</div> : null}
          {loading ? <div className="rounded-3xl bg-white p-5 text-slate-500 shadow-sm">Loading live backend data…</div> : null}
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" id="dashboard">
            <StatCard icon="💳" label="Revenue" value={money(dashboard?.metrics[0]?.value ?? 0)} hint={dashboard?.metrics[0]?.trend ?? 'Current period'} tone="green" />
            <StatCard icon="👥" label="Clients" value={String(clients.length)} hint="Recently active accounts" />
            <StatCard icon="📦" label="Low stock" value={String(lowStockCount)} hint="Products below minimum level" tone={lowStockCount ? 'red' : 'green'} />
            <StatCard icon="⛑️" label="PPE compliance" value={`${ppeCompliance?.compliance_rate ?? 0}%`} hint={`${ppeCompliance?.overdue_replacements ?? 0} overdue replacements`} tone="amber" />
          </section>
          <DataTable title="Clients" description="Customer accounts from the backend API." rows={clients} getKey={(row) => row.uuid} columns={[{ header: 'Client', render: (row) => <strong>{row.company_name}</strong> }, { header: 'Number', render: (row) => row.client_number }, { header: 'Status', render: (row) => row.status }, { header: 'Credit limit', render: (row) => money(row.credit_limit) }]} />
          <DataTable title="Inventory" description="Product stock and ZAR pricing." rows={products} getKey={(row) => row.uuid} columns={[{ header: 'SKU', render: (row) => row.sku }, { header: 'Product', render: (row) => <strong>{row.name}</strong> }, { header: 'Stock', render: (row) => `${row.current_stock} ${row.unit_of_measure}` }, { header: 'Selling price', render: (row) => money(row.selling_price) }, { header: 'Status', render: (row) => row.is_low_stock ? <span className="pill danger">Low stock</span> : <span className="pill success">OK</span> }]} />
          <div className="grid gap-6 xl:grid-cols-2" id="ppe-compliance">
            <DataTable title="PPE Items" rows={ppeItems.slice(0, 6)} getKey={(row) => row.uuid} columns={[{ header: 'Item', render: (row) => <strong>{row.name}</strong> }, { header: 'Category', render: (row) => row.category_name }, { header: 'Stock', render: (row) => row.current_stock }, { header: 'Status', render: (row) => row.status }]} />
            <DataTable title="PPE Issues" rows={ppeIssues.slice(0, 6)} getKey={(row) => row.uuid} columns={[{ header: 'Employee', render: (row) => row.employee_name }, { header: 'Item', render: (row) => row.ppe_item_name }, { header: 'Due', render: (row) => row.replacement_due_date ?? 'N/A' }, { header: 'Status', render: (row) => row.is_overdue ? <span className="pill danger">Overdue</span> : row.status }]} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
