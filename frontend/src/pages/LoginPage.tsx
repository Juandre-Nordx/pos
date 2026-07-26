import { FormEvent, useState } from 'react';
import { login, storeTokens } from '../api/client';

type LoginPageProps = {
  onLogin: () => void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState('admin@demo.nordxpos.co.za');
  const [password, setPassword] = useState('Demo@2026!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const tokens = await login(email, password);
      storeTokens(tokens.access_token, tokens.refresh_token);
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-slate-950 px-4 py-10 text-white">
      <section className="w-full max-w-md rounded-3xl border border-white/10 bg-white p-8 text-slate-950 shadow-2xl">
        <div className="mb-8 flex items-center gap-3">
          <div className="rounded-2xl bg-blue-600 p-3 text-white"><span aria-hidden="true">🛡️</span></div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-600">NordxPOS</p>
            <h1 className="text-2xl font-bold">Sign in to your workspace</h1>
          </div>
        </div>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-700">
            Email
            <input className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-blue-600 transition focus:ring-2" value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Password
            <input className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none ring-blue-600 transition focus:ring-2" value={password} onChange={(event) => setPassword(event.target.value)} type="password" />
          </label>
          {error ? <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}
          <button className="w-full rounded-2xl bg-blue-600 px-4 py-3 font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70" disabled={loading} type="submit">
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </section>
    </main>
  );
}
