import { FormEvent, useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import { DataTable } from '../components/DataTable';
import type { Supplier, SupplierCreate } from '../types/api';

const emptySupplier: SupplierCreate = {
  name: '', code: '', contact_person: '', contact_email: '', phone: '', city: '', country: 'South Africa',
  payment_terms_days: 30, lead_time_days: 0, is_active: true, contacts: [],
};

export function SuppliersPage({ canManage }: { canManage: boolean }) {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState<SupplierCreate>(emptySupplier);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pendingDeactivation, setPendingDeactivation] = useState<Supplier | null>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    try { setSuppliers(await api.suppliers()); } catch (err) { setError(err instanceof Error ? err.message : 'Unable to load suppliers.'); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, []);
  const visible = useMemo(() => suppliers.filter((supplier) =>
    [supplier.name, supplier.code, supplier.contact_person ?? '', supplier.contact_email ?? '', supplier.phone ?? '']
      .some((value) => value.toLowerCase().includes(search.trim().toLowerCase()))), [suppliers, search]);

  async function submit(event: FormEvent) {
    event.preventDefault(); setSaving(true); setError('');
    try {
      await api.createSupplier(form); await load(); setForm(emptySupplier); setOpen(false);
      setMessage('Supplier created successfully.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Supplier could not be created.'); }
    finally { setSaving(false); }
  }

  async function deactivate(supplier: Supplier) {
    try { await api.deactivateSupplier(supplier.uuid); await load(); setMessage('Supplier deactivated.'); }
    catch (err) { setError(err instanceof Error ? err.message : 'Supplier could not be deactivated.'); }
    finally { setPendingDeactivation(null); }
  }

  return <section className="stock-page">
    <div className="page-heading"><div><span className="eyebrow">Purchasing</span><h2>Suppliers</h2><p>Manage supplier records and contacts without removing transaction history.</p></div>
      {canManage ? <button className="primary-button" onClick={() => setOpen(true)}>+ Add supplier</button> : null}</div>
    {message ? <p className="notice success-notice" role="status">{message}</p> : null}
    {error ? <p className="notice error-notice" role="alert">{error}</p> : null}
    <label className="stock-search"><span>Search suppliers</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Name, code, contact, email or phone" /></label>
    {loading ? <p className="notice">Loading suppliers…</p> : <DataTable title="All suppliers" description={`${visible.length} suppliers shown`} rows={visible} getKey={(row) => row.uuid} emptyText="No suppliers match your search." columns={[
      { header: 'Supplier', render: (row) => <><strong>{row.name}</strong><small>{row.code}</small></> },
      { header: 'Main contact', render: (row) => <>{row.contact_person || 'Not set'}<small>{row.contact_email || row.phone || 'No contact details'}</small></> },
      { header: 'Location', render: (row) => [row.city, row.country].filter(Boolean).join(', ') || 'Not set' },
      { header: 'Status', render: (row) => row.is_active ? <span className="pill success">Active</span> : <span className="pill danger">Inactive</span> },
      ...(canManage ? [{ header: 'Action', render: (row: Supplier) => row.is_active ? <button className="table-action" onClick={() => setPendingDeactivation(row)}>Deactivate</button> : null }] : []),
    ]} />}
    {open ? <div className="modal-backdrop"><section className="stock-dialog supplier-dialog" role="dialog" aria-modal="true" aria-labelledby="supplier-title">
      <div className="dialog-heading"><div><span className="eyebrow">New record</span><h3 id="supplier-title">Add supplier</h3></div><button className="close-button" onClick={() => setOpen(false)}>×</button></div>
      <form onSubmit={submit}><div className="form-grid">
        <label><span>Supplier name *</span><input required value={form.name} onChange={(e) => setForm({...form, name:e.target.value})}/></label>
        <label><span>Supplier code *</span><input required value={form.code} onChange={(e) => setForm({...form, code:e.target.value.toUpperCase()})}/></label>
        <label><span>Contact person</span><input value={form.contact_person} onChange={(e) => setForm({...form, contact_person:e.target.value})}/></label>
        <label><span>Email</span><input type="email" value={form.contact_email} onChange={(e) => setForm({...form, contact_email:e.target.value})}/></label>
        <label><span>Phone</span><input value={form.phone} onChange={(e) => setForm({...form, phone:e.target.value})}/></label>
        <label><span>City</span><input value={form.city} onChange={(e) => setForm({...form, city:e.target.value})}/></label>
      </div><div className="dialog-actions"><button type="button" className="secondary-button" onClick={() => setOpen(false)}>Cancel</button><button className="primary-button" disabled={saving}>{saving ? 'Saving…' : 'Create supplier'}</button></div></form>
    </section></div> : null}
    {pendingDeactivation ? <div className="modal-backdrop"><section className="stock-dialog" role="alertdialog" aria-modal="true" aria-labelledby="deactivate-title">
      <div className="dialog-heading"><div><span className="eyebrow">Confirmation required</span><h3 id="deactivate-title">Deactivate supplier?</h3></div></div>
      <p>{pendingDeactivation.name} will no longer be available for new purchasing, but all historical records will be retained.</p>
      <div className="dialog-actions"><button className="secondary-button" onClick={() => setPendingDeactivation(null)}>Keep active</button><button className="primary-button" onClick={() => void deactivate(pendingDeactivation)}>Deactivate</button></div>
    </section></div> : null}
  </section>;
}
