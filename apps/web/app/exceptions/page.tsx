'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  createEvidencePacket,
  fetchDistricts,
  fetchExceptions,
  updateException,
} from '../../lib/api';

export default function ExceptionsPage() {
  const queryClient = useQueryClient();
  const { data: districts } = useQuery({ queryKey: ['districts'], queryFn: fetchDistricts });
  const activeDistrict = useMemo(() => districts?.[0], [districts]);

  const { data: exceptions } = useQuery({
    queryKey: ['exceptions', activeDistrict?.id],
    queryFn: () => fetchExceptions(activeDistrict!.id),
    enabled: Boolean(activeDistrict?.id),
  });

  const [selected, setSelected] = useState<string[]>([]);

  const updateMutation = useMutation({
    mutationFn: (params: { exceptionId: string; status: string }) =>
      updateException(activeDistrict!.id, params.exceptionId, { status: params.status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['exceptions'] }),
  });

  const evidenceMutation = useMutation({
    mutationFn: () =>
      createEvidencePacket(activeDistrict!.id, {
        name: `Packet ${new Date().toLocaleString()}`,
        description: 'Auto-generated evidence packet',
        exception_ids: selected,
      }),
    onSuccess: () => {
      setSelected([]);
    },
  });

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-4xl px-6 py-10 space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <Link href="/" className="text-sm text-slate-400 underline decoration-dotted underline-offset-4">
              ← Back to dashboard
            </Link>
            <h1 className="mt-2 text-2xl font-semibold text-white">Exceptions</h1>
            <p className="text-sm text-slate-400">Track outstanding rule results and generate evidence packets.</p>
          </div>
          <button
            type="button"
            disabled={selected.length === 0 || evidenceMutation.isLoading}
            onClick={() => evidenceMutation.mutate()}
            className="rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow disabled:cursor-not-allowed disabled:bg-indigo-800"
          >
            {evidenceMutation.isLoading ? 'Generating…' : `Generate Packet (${selected.length})`}
          </button>
        </header>

        <div className="rounded-lg border border-slate-800 bg-slate-900/70">
          <table className="min-w-full divide-y divide-slate-800 text-sm">
            <thead className="text-left text-slate-400">
              <tr>
                <th className="px-3 py-2">
                  <span className="sr-only">Select</span>
                </th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Rationale</th>
                <th className="px-3 py-2">Due Date</th>
                <th className="px-3 py-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {exceptions?.map((exception) => (
                <tr key={exception.id}>
                  <td className="px-3 py-2 align-top">
                    <input
                      type="checkbox"
                      checked={selected.includes(exception.id)}
                      onChange={(event) =>
                        setSelected((prev) =>
                          event.target.checked ? [...prev, exception.id] : prev.filter((id) => id !== exception.id),
                        )
                      }
                    />
                  </td>
                  <td className="px-3 py-2 align-top">{exception.status}</td>
                  <td className="px-3 py-2 align-top text-slate-300">
                    {exception.rationale ?? '—'}
                  </td>
                  <td className="px-3 py-2 align-top text-slate-300">
                    {exception.due_date ?? '—'}
                  </td>
                  <td className="px-3 py-2 align-top">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => updateMutation.mutate({ exceptionId: exception.id, status: 'in_review' })}
                        className="rounded border border-slate-700 px-2 py-1 text-xs"
                      >
                        In Review
                      </button>
                      <button
                        type="button"
                        onClick={() => updateMutation.mutate({ exceptionId: exception.id, status: 'resolved' })}
                        className="rounded border border-slate-700 px-2 py-1 text-xs"
                      >
                        Resolve
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {(!exceptions || exceptions.length === 0) && (
                <tr>
                  <td colSpan={5} className="px-3 py-6 text-center text-slate-400">
                    No exceptions yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
