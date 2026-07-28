import { useEffect, useMemo, useState } from 'react';
import { api, clearTokens, getStoredToken } from './api/client';
import { DataTable } from './components/DataTable';
import { CompanySettingsForm } from './components/CompanySettingsForm';
import { StatCard } from './components/StatCard';
import { LoginPage } from './pages/LoginPage';
import { StockPage } from './pages/StockPage';
import { SuppliersPage } from './pages/SuppliersPage';
import type { Client, CompanySettings, Dashboard, PPECompliance, PPEItem, Product, User } from './types/api';
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
  const [companySettings, setCompanySettings] = useState<CompanySettings | null>(null);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [page, setPage] = useState(window.location.hash === '#stock' ? 'stock' : 'dashboard');

  async function loadProducts() {
    setProducts(await api.products('', false, 100));
  }

  useEffect(() => {
    if (!token) return;
    let active = true;
    setLoading(true);
    setError('');
    Promise.all([api.me(), api.dashboard(), api.clients(search), api.products(search, false, 100), api.ppeCompliance(), api.ppeItems(), api.companySettings()])
      .then(([me, dash, clientRows, productRows, compliance, itemRows, company]) => {
        if (!active) return;
        setUser(me);
        setDashboard(dash);
        setClients(clientRows);
        setProducts(productRows);
        setPpeCompliance(compliance);
        setPpeItems(itemRows);
        setCompanySettings(company);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Unable to load dashboard'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [token, search]);

  function navigate(nextPage: string) {
    setPage(nextPage);
    window.location.hash = nextPage;
    setMobileMenuOpen(false);
  }

  const lowStockCount = useMemo(() => products.filter((product) => product.is_low_stock).length, [products]);
  const canAddStock = user?.roles.some((role) => ['super_admin', 'director', 'store', 'manager'].includes(role)) ?? false;

  async function saveCompanySettings(settings: CompanySettings) {
    setSavingSettings(true); setError('');
    try { setCompanySettings(await api.updateCompanySettings(settings)); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to save company details'); throw err; }
    finally { setSavingSettings(false); }
  }

  if (!token) return <LoginPage onLogin={() => setToken(getStoredToken())} />;

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <aside className={`app-sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="flex items-center gap-3"><div className="rounded-2xl bg-blue-500 p-3"><span aria-hidden="true">🛡️</span></div><div><p className="text-xs uppercase tracking-[0.35em] text-blue-200">Nordx</p><h1 className="text-xl font-bold">POS ERP</h1></div></div>
        <nav className="mt-10 space-y-2 text-sm font-medium text-slate-300">
          <button className={page === 'dashboard' ? 'nav-link active' : 'nav-link'} onClick={() => navigate('dashboard')}>Dashboard</button>
          <button className={page === 'stock' ? 'nav-link active' : 'nav-link'} onClick={() => navigate('stock')}>Stock</button>
          <p className="nav-section">Suppliers</p>
          <button className={page === 'suppliers' ? 'nav-link active' : 'nav-link'} onClick={() => navigate('suppliers')}>All suppliers</button>
        </nav>
        <button className="mt-auto flex items-center gap-2 rounded-2xl px-4 py-3 text-left text-sm text-slate-300 hover:bg-white/10" onClick={() => { clearTokens(); setToken(null); }}><span aria-hidden="true">↩</span> Sign out</button>
      </aside>
      <main className="lg:pl-72">
        <header className="app-header">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="header-title"><button className="menu-button" aria-label="Open navigation" aria-expanded={mobileMenuOpen} onClick={() => setMobileMenuOpen((open) => !open)}>☰</button><div><p className="text-sm text-slate-500">Welcome back{user ? `, ${user.first_name}` : ''}</p><h2 className="text-2xl font-bold">{page === 'stock' ? 'Inventory' : page === 'suppliers' ? 'Supplier management' : 'Operations dashboard'}</h2></div></div>
            {page === 'dashboard' ? <label className="flex w-full max-w-md items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500"><span aria-hidden="true">🔎</span><input className="w-full outline-none" placeholder="Search clients and inventory…" value={search} onChange={(event) => setSearch(event.target.value)} /></label> : null}
          </div>
        </header>
        <div className="dashboard-content">
          {error ? <div className="rounded-3xl border border-red-200 bg-red-50 p-5 text-red-700">{error}</div> : null}
          {loading ? <div className="rounded-3xl bg-white p-5 text-slate-500 shadow-sm">Loading live backend data…</div> : null}
          {page === 'stock' ? <StockPage products={products} loading={loading} canAddStock={canAddStock} onStockAdded={loadProducts} /> : page === 'suppliers' ? <SuppliersPage canManage={user?.roles.some((role) => ['super_admin', 'director', 'manager'].includes(role)) ?? false} /> : <><section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" id="dashboard">
            <StatCard icon="💳" label="Revenue" value={money(dashboard?.metrics[0]?.value ?? 0)} hint={dashboard?.metrics[0]?.trend ?? 'Current period'} tone="green" />
            <StatCard icon="👥" label="Clients" value={String(clients.length)} hint="Recently active accounts" />
            <StatCard icon="📦" label="Low stock" value={String(lowStockCount)} hint="Products below minimum level" tone={lowStockCount ? 'red' : 'green'} />
            <StatCard icon="⛑️" label="PPE compliance" value={`${ppeCompliance?.compliance_rate ?? 0}%`} hint={`${ppeCompliance?.overdue_replacements ?? 0} overdue replacements`} tone="amber" />
          </section>
          <div id="clients"><DataTable title="Clients" description="Customer accounts from the backend API." rows={clients} getKey={(row) => row.uuid} columns={[{ header: 'Client', render: (row) => <strong>{row.company_name}</strong> }, { header: 'Number', render: (row) => row.client_number }, { header: 'Status', render: (row) => row.status }, { header: 'Credit limit', render: (row) => money(row.credit_limit) }]} /></div>
          <div id="inventory"><DataTable title="Inventory" description="Product stock and ZAR pricing." rows={products} getKey={(row) => row.uuid} columns={[{ header: 'SKU', render: (row) => row.sku }, { header: 'Product', render: (row) => <strong>{row.name}</strong> }, { header: 'Stock', render: (row) => `${row.current_stock} ${row.unit_of_measure}` }, { header: 'Selling price', render: (row) => money(row.selling_price) }, { header: 'Status', render: (row) => row.is_low_stock ? <span className="pill danger">Low stock</span> : <span className="pill success">OK</span> }]} /></div>
          <div id="ppe-compliance"><DataTable title="PPE Items" rows={ppeItems.slice(0, 6)} getKey={(row) => row.uuid} columns={[{ header: 'Item', render: (row) => <strong>{row.name}</strong> }, { header: 'Category', render: (row) => row.category_name }, { header: 'Stock', render: (row) => row.current_stock }, { header: 'Status', render: (row) => row.status }]} /></div>
          <CompanySettingsForm settings={companySettings} saving={savingSettings} onSave={saveCompanySettings} />
          </>}
        </div>
      </main>
      {mobileMenuOpen ? <button className="sidebar-scrim" aria-label="Close navigation" onClick={() => setMobileMenuOpen(false)} /> : null}
    </div>
  );
}

export default App;
