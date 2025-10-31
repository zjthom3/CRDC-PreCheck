'use client';

import { FormEvent, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';

import { fetchDistricts, loginSSO } from '../../lib/api';

export default function LoginPage() {
  const router = useRouter();
  const { data: districts } = useQuery({ queryKey: ['districts'], queryFn: fetchDistricts });
  const district = useMemo(() => districts?.[0], [districts]);

  const [provider, setProvider] = useState('clever');
  const [subject, setSubject] = useState('demo-admin');
  const [email, setEmail] = useState('admin@demo.edu');
  const [displayName, setDisplayName] = useState('Demo Admin');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!district || loading) return;

    setLoading(true);
    setError(null);
    try {
      await loginSSO(district.id, { provider, subject, email, display_name: displayName });
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto mt-16 max-w-md rounded-lg border border-slate-800 bg-slate-900/70 p-6 shadow">
        <h1 className="text-2xl font-semibold text-white">Single Sign-On</h1>
        <p className="mt-2 text-sm text-slate-400">Simulated Clever/ClassLink SSO for pilot environments.</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <label className="flex flex-col text-sm text-slate-300">
            <span className="mb-1 text-slate-200">Provider</span>
            <input
              value={provider}
              onChange={(event) => setProvider(event.target.value)}
              className="rounded border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
            />
          </label>
          <label className="flex flex-col text-sm text-slate-300">
            <span className="mb-1 text-slate-200">Subject</span>
            <input
              value={subject}
              onChange={(event) => setSubject(event.target.value)}
              className="rounded border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
            />
          </label>
          <label className="flex flex-col text-sm text-slate-300">
            <span className="mb-1 text-slate-200">Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="rounded border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
            />
          </label>
          <label className="flex flex-col text-sm text-slate-300">
            <span className="mb-1 text-slate-200">Display Name</span>
            <input
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              className="rounded border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100"
            />
          </label>

          <button
            type="submit"
            disabled={!district || loading}
            className="w-full rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow disabled:cursor-not-allowed disabled:bg-indigo-800"
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        {error && <p className="mt-4 text-sm text-rose-400">{error}</p>}
      </div>
    </main>
  );
}
