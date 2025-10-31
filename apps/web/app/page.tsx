'use client';

import Link from 'next/link';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  fetchDistricts,
  fetchReadiness,
  fetchRuleResults,
  fetchRuleRuns,
  triggerPowerschoolSync,
  triggerRuleRun,
} from '../lib/api';

export default function HomePage() {
  const queryClient = useQueryClient();

  const { data: districts, isLoading: districtsLoading } = useQuery({
    queryKey: ['districts'],
    queryFn: fetchDistricts,
  });

  const activeDistrict = districts?.[0];

  const {
    data: ruleRuns,
    isLoading: runsLoading,
    refetch: refetchRuleRuns,
  } = useQuery({
    queryKey: ['ruleRuns', activeDistrict?.id],
    queryFn: () => fetchRuleRuns(activeDistrict!.id),
    enabled: Boolean(activeDistrict?.id),
  });

  const latestRuleRun = ruleRuns?.[0];

  const { data: ruleResults, isLoading: resultsLoading } = useQuery({
    queryKey: ['ruleResults', activeDistrict?.id, latestRuleRun?.id],
    queryFn: () => fetchRuleResults(activeDistrict!.id, latestRuleRun?.id),
    enabled: Boolean(activeDistrict?.id),
  });

  const { data: readinessData } = useQuery({
    queryKey: ['readiness', activeDistrict?.id],
    queryFn: () => fetchReadiness(activeDistrict!.id),
    enabled: Boolean(activeDistrict?.id),
  });

  const validateMutation = useMutation({
    mutationFn: () => triggerRuleRun(activeDistrict!.id),
    onSuccess: async () => {
      await refetchRuleRuns();
      await queryClient.invalidateQueries({ queryKey: ['ruleResults'] });
    },
  });

  const syncMutation = useMutation({
    mutationFn: () => triggerPowerschoolSync(activeDistrict!.id),
    onSuccess: async () => {
      await refetchRuleRuns();
      await queryClient.invalidateQueries({ queryKey: ['ruleResults'] });
    },
  });

  const isLoading = districtsLoading || runsLoading || resultsLoading;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-4xl px-6 py-12 space-y-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold">CRDC PreCheck</h1>
            <p className="text-slate-400">
              Validate CRDC readiness across districts before official submission.
            </p>
            <div className="mt-3 flex gap-3 text-sm text-slate-400">
              <Link href="/import" className="underline decoration-dotted underline-offset-4">
                Import students from CSV
              </Link>
              <span aria-hidden="true">•</span>
              <button
                type="button"
                className="underline decoration-dotted underline-offset-4"
                onClick={() => syncMutation.mutate()}
                disabled={!activeDistrict || syncMutation.isLoading}
              >
                {syncMutation.isLoading ? 'Syncing…' : 'Sync PowerSchool'}
              </button>
              <span aria-hidden="true">•</span>
              <Link href="/exceptions" className="underline decoration-dotted underline-offset-4">
                View exceptions
              </Link>
            </div>
          </div>
          <button
            type="button"
            disabled={!activeDistrict || validateMutation.isLoading}
            onClick={() => validateMutation.mutate()}
            className="rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow disabled:cursor-not-allowed disabled:bg-indigo-800"
          >
            {validateMutation.isLoading ? 'Running...' : 'Run Validation'}
          </button>
        </header>

        <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-6">
          <h2 className="text-xl font-medium text-white">Latest Results</h2>
          {syncMutation.isSuccess && (
            <p className="mt-2 text-xs text-emerald-400">PowerSchool sync triggered successfully.</p>
          )}
          {validateMutation.isSuccess && (
            <p className="mt-2 text-xs text-emerald-400">Validation queued successfully.</p>
          )}
          {isLoading && <p className="mt-4 text-slate-400">Loading data...</p>}
          {!isLoading && (!ruleResults || ruleResults.length === 0) && (
            <p className="mt-4 text-slate-400">No rule results yet. Run a validation to see findings.</p>
          )}
          {!isLoading && ruleResults && ruleResults.length > 0 && (
            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-800 text-left text-sm">
                <thead>
                  <tr className="text-slate-400">
                    <th className="px-3 py-2">Severity</th>
                    <th className="px-3 py-2">Message</th>
                    <th className="px-3 py-2">Status</th>
                    <th className="px-3 py-2">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {ruleResults.map((result) => (
                    <tr key={result.id}>
                      <td className="px-3 py-2">
                        <span
                          className={`inline-flex items-center rounded px-2 py-1 text-xs font-medium ${
                            result.severity === 'error'
                              ? 'bg-rose-500/20 text-rose-300'
                              : result.severity === 'warning'
                              ? 'bg-amber-500/20 text-amber-300'
                              : 'bg-slate-500/20 text-slate-200'
                          }`}
                        >
                          {result.severity.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-slate-200">{result.message}</td>
                      <td className="px-3 py-2 text-slate-300">{result.status}</td>
                      <td className="px-3 py-2 text-slate-300">
                        {new Date(result.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-6">
          <h2 className="text-xl font-medium text-white">Readiness Heatmap</h2>
          {readinessData && readinessData.items.length > 0 ? (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-800 text-left text-sm">
                <thead>
                  <tr className="text-slate-400">
                    <th className="px-3 py-2">Scope</th>
                    <th className="px-3 py-2">Category</th>
                    <th className="px-3 py-2">Score</th>
                    <th className="px-3 py-2">Open Errors</th>
                    <th className="px-3 py-2">Open Warnings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {readinessData.items.map((item) => (
                    <tr key={`${item.category}-${item.school_id ?? 'district'}`}>
                      <td className="px-3 py-2 text-slate-200">{item.school_name ?? 'District'}</td>
                      <td className="px-3 py-2 text-slate-300">{item.category}</td>
                      <td className="px-3 py-2 text-slate-200">{item.score}</td>
                      <td className="px-3 py-2 text-slate-300">{item.open_errors}</td>
                      <td className="px-3 py-2 text-slate-300">{item.open_warnings}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="mt-4 text-slate-400">Run a validation to generate readiness metrics.</p>
          )}
        </section>
      </div>
    </main>
  );
}
