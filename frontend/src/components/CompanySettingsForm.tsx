import { type FormEvent, useEffect, useState } from 'react';
import type { CompanySettings } from '../types/api';

const emptySettings: CompanySettings = {
  company_name: '', trading_name: '', registration_number: '', vat_number: '', email: '', phone: '', website: '', logo_url: '',
  address: { street: '', city: '', province: '', postal_code: '', country: 'South Africa' },
};

type Props = { settings: CompanySettings | null; saving: boolean; onSave: (settings: CompanySettings) => Promise<void> };

export function CompanySettingsForm({ settings, saving, onSave }: Props) {
  const [form, setForm] = useState<CompanySettings>(emptySettings);
  const [saved, setSaved] = useState(false);
  useEffect(() => setForm(settings ? { ...emptySettings, ...settings, address: { ...emptySettings.address, ...settings.address } } : emptySettings), [settings]);

  const update = (field: keyof CompanySettings, value: string) => { setSaved(false); setForm((old) => ({ ...old, [field]: value })); };
  const updateAddress = (field: keyof CompanySettings['address'], value: string) => { setSaved(false); setForm((old) => ({ ...old, address: { ...old.address, [field]: value } })); };
  async function submit(event: FormEvent) {
    event.preventDefault();
    try { await onSave(form); setSaved(true); } catch { /* The dashboard displays the API error. */ }
  }

  return <section className="settings-card" id="settings">
    <div className="settings-heading"><div><span className="eyebrow">Business profile</span><h2>Company details</h2><p>These details will appear on your invoices and customer documents.</p></div>
      <div className="logo-preview" aria-label="Company logo preview">{form.logo_url ? <img src={form.logo_url} alt={`${form.company_name || 'Company'} logo`} /> : <span>Logo</span>}</div>
    </div>
    <form className="settings-form" onSubmit={submit}>
      <div className="form-grid">
        <label><span>Company name *</span><input required value={form.company_name} onChange={(e) => update('company_name', e.target.value)} placeholder="Acme (Pty) Ltd" /></label>
        <label><span>Trading name</span><input value={form.trading_name ?? ''} onChange={(e) => update('trading_name', e.target.value)} placeholder="Acme Supplies" /></label>
        <label><span>VAT number</span><input value={form.vat_number ?? ''} onChange={(e) => update('vat_number', e.target.value)} placeholder="4XXXXXXXXX" /></label>
        <label><span>Registration number</span><input value={form.registration_number ?? ''} onChange={(e) => update('registration_number', e.target.value)} placeholder="2026/000000/07" /></label>
        <label><span>Billing email</span><input type="email" value={form.email ?? ''} onChange={(e) => update('email', e.target.value)} placeholder="accounts@company.co.za" /></label>
        <label><span>Phone</span><input value={form.phone ?? ''} onChange={(e) => update('phone', e.target.value)} placeholder="+27 11 000 0000" /></label>
        <label><span>Website</span><input type="url" value={form.website ?? ''} onChange={(e) => update('website', e.target.value)} placeholder="https://company.co.za" /></label>
        <label><span>Logo URL</span><input type="url" value={form.logo_url ?? ''} onChange={(e) => update('logo_url', e.target.value)} placeholder="https://company.co.za/logo.png" /></label>
      </div>
      <div className="form-section"><h3>Business address</h3><div className="form-grid">
        <label className="span-two"><span>Street address</span><input value={form.address.street} onChange={(e) => updateAddress('street', e.target.value)} placeholder="12 Market Street" /></label>
        <label><span>City</span><input value={form.address.city} onChange={(e) => updateAddress('city', e.target.value)} placeholder="Johannesburg" /></label>
        <label><span>Province</span><input value={form.address.province} onChange={(e) => updateAddress('province', e.target.value)} placeholder="Gauteng" /></label>
        <label><span>Postal code</span><input value={form.address.postal_code} onChange={(e) => updateAddress('postal_code', e.target.value)} placeholder="2000" /></label>
        <label><span>Country</span><input value={form.address.country} onChange={(e) => updateAddress('country', e.target.value)} /></label>
      </div></div>
      <div className="form-actions">{saved ? <span className="save-confirmation">✓ Company details saved</span> : <span>Fields marked * are required</span>}<button className="primary-button" disabled={saving} type="submit">{saving ? 'Saving…' : 'Save company details'}</button></div>
    </form>
  </section>;
}
