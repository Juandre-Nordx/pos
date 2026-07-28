import { FormEvent, useMemo, useState } from 'react';
import { api } from '../api/client';
import { DataTable } from '../components/DataTable';
import type { Product } from '../types/api';

type StockPageProps = {
  products: Product[];
  loading: boolean;
  canAddStock: boolean;
  onStockAdded: () => Promise<void>;
};

export function StockPage({ products, loading, canAddStock, onStockAdded }: StockPageProps) {
  const [search, setSearch] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [reason, setReason] = useState('Stock received');
  const [reference, setReference] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const visibleProducts = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return products;
    return products.filter((product) =>
      [product.name, product.sku, product.barcode ?? ''].some((value) => value.toLowerCase().includes(query)),
    );
  }, [products, search]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!selectedProduct || submitting) return;
    setSubmitting(true);
    setError('');
    setMessage('');
    try {
      const movement = await api.addStock(selectedProduct.uuid, quantity, reason.trim(), reference.trim());
      await onStockAdded();
      setMessage(`${movement.quantity_added} units added to ${selectedProduct.name}. New stock: ${movement.quantity_after}.`);
      setSelectedProduct(null);
      setQuantity(1);
      setReference('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Stock could not be added.');
    } finally {
      setSubmitting(false);
    }
  }

  return <section className="stock-page" aria-labelledby="stock-title">
    <div className="page-heading">
      <div><span className="eyebrow">Inventory management</span><h2 id="stock-title">Stock</h2><p>Review availability and receive products into the main warehouse.</p></div>
      {canAddStock ? <button className="primary-button" onClick={() => setSelectedProduct(products[0] ?? null)} disabled={!products.length}>+ Add stock</button> : null}
    </div>
    {message ? <p className="notice success-notice" role="status">{message}</p> : null}
    {error ? <p className="notice error-notice" role="alert">{error}</p> : null}
    <label className="stock-search"><span>Search stock</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Product name, SKU or barcode" /></label>
    {loading ? <p className="notice">Loading stock…</p> : <DataTable title="All products" description={`${visibleProducts.length} products shown`} rows={visibleProducts} getKey={(row) => row.uuid} emptyText="No products match your search." columns={[
      { header: 'SKU / barcode', render: (row) => <><strong>{row.sku}</strong><small>{row.barcode || 'No barcode'}</small></> },
      { header: 'Product', render: (row) => <><strong>{row.name}</strong><small>{row.category_name || 'Uncategorised'}</small></> },
      { header: 'On hand', render: (row) => `${row.current_stock} ${row.unit_of_measure}` },
      { header: 'Reorder level', render: (row) => row.min_stock_level },
      { header: 'Status', render: (row) => row.is_low_stock ? <span className="pill danger">Low stock</span> : <span className="pill success">In stock</span> },
      ...(canAddStock ? [{ header: 'Action', render: (row: Product) => <button className="table-action" onClick={() => { setSelectedProduct(row); setMessage(''); setError(''); }}>Add stock</button> }] : []),
    ]} />}
    {selectedProduct ? <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !submitting) setSelectedProduct(null); }}>
      <section className="stock-dialog" role="dialog" aria-modal="true" aria-labelledby="add-stock-title">
        <div className="dialog-heading"><div><span className="eyebrow">Receive inventory</span><h3 id="add-stock-title">Add stock</h3></div><button className="close-button" aria-label="Close add stock form" onClick={() => setSelectedProduct(null)} disabled={submitting}>×</button></div>
        <form onSubmit={submit}>
          <label><span>Product</span><select value={selectedProduct.uuid} onChange={(event) => setSelectedProduct(products.find((item) => item.uuid === event.target.value) ?? null)}>{products.map((product) => <option value={product.uuid} key={product.uuid}>{product.name} ({product.sku})</option>)}</select></label>
          <div className="current-stock">Current stock <strong>{selectedProduct.current_stock} {selectedProduct.unit_of_measure}</strong></div>
          <label><span>Quantity to add *</span><input autoFocus required type="number" min="1" max="1000000" step="1" value={quantity} onChange={(event) => setQuantity(Number(event.target.value))} /></label>
          <label><span>Reason *</span><input required minLength={3} maxLength={500} value={reason} onChange={(event) => setReason(event.target.value)} /></label>
          <label><span>Supplier reference</span><input maxLength={100} value={reference} onChange={(event) => setReference(event.target.value)} placeholder="PO or delivery note number" /></label>
          <div className="dialog-actions"><button type="button" className="secondary-button" onClick={() => setSelectedProduct(null)} disabled={submitting}>Cancel</button><button type="submit" className="primary-button" disabled={submitting || quantity < 1 || reason.trim().length < 3}>{submitting ? 'Adding…' : 'Add stock'}</button></div>
        </form>
      </section>
    </div> : null}
  </section>;
}
