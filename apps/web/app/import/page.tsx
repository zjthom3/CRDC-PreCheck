'use client';

import { FormEvent, useMemo, useState } from 'react';
import Link from 'next/link';
import { useMutation, useQuery } from '@tanstack/react-query';

import {
  CsvImportResponse,
  StudentCsvMapping,
  fetchDistricts,
  uploadStudentCsv,
} from '../../lib/api';

const DEFAULT_MAPPING: StudentCsvMapping = {
  sis_id: 'Student ID',
  first_name: 'First Name',
  last_name: 'Last Name',
  grade_level: 'Grade',
  school_name: 'School',
  enrollment_status: 'Enrollment Status',
  ell_status: 'ELL',
  idea_flag: 'IDEA',
};

export default function ImportPage() {
  const { data: districts } = useQuery({ queryKey: ['districts'], queryFn: fetchDistricts });
  const activeDistrict = useMemo(() => districts?.[0], [districts]);

  const [mapping, setMapping] = useState<StudentCsvMapping>(DEFAULT_MAPPING);
  const [file, setFile] = useState<File | null>(null);

  const importMutation = useMutation({
    mutationFn: ({ districtId, file, mapping }: { districtId: string; file: File; mapping: StudentCsvMapping }) =>
      uploadStudentCsv(districtId, file, mapping),
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!activeDistrict || !file) {
      return;
    }
    importMutation.mutate({ districtId: activeDistrict.id, file, mapping });
  };

  const result: CsvImportResponse | undefined = importMutation.data;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-3xl px-6 py-10 space-y-8">
        <header>
          <Link href="/" className="text-sm text-slate-400 underline decoration-dotted underline-offset-4">
            ← Back to dashboard
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-white">Import Students from CSV</h1>
          <p className="mt-1 text-sm text-slate-400">
            Map your CSV columns to the canonical student fields and upload. Existing students with matching SIS IDs
            will be updated.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-slate-800 bg-slate-900/70 p-6">
          <fieldset className="grid gap-3 md:grid-cols-2">
            {(
              Object.entries(mapping) as Array<[keyof StudentCsvMapping, string | undefined]>
            ).map(([field, value]) => (
              <label key={field} className="flex flex-col text-sm text-slate-300">
                <span className="mb-1 font-medium text-slate-200">{field.replace('_', ' ')}</span>
                <input
                  type="text"
                  value={value ?? ''}
                  onChange={(event) =>
                    setMapping((prev) => ({
                      ...prev,
                      [field]: event.target.value,
                    }))
                  }
                  placeholder="Column name"
                  className="rounded border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </label>
            ))}
          </fieldset>

          <label className="flex flex-col text-sm text-slate-300">
            <span className="mb-1 font-medium text-slate-200">CSV File</span>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              className="rounded border border-dashed border-slate-700 bg-slate-950 px-3 py-4 text-slate-100"
            />
          </label>

          <button
            type="submit"
            disabled={!activeDistrict || !file || importMutation.isLoading}
            className="rounded bg-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow disabled:cursor-not-allowed disabled:bg-indigo-800"
          >
            {importMutation.isLoading ? 'Importing…' : 'Start Import'}
          </button>
        </form>

        {result && (
          <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-6 text-sm text-slate-200">
            <h2 className="text-lg font-semibold text-white">Import Summary</h2>
            <dl className="mt-4 grid grid-cols-2 gap-3">
              <div>
                <dt className="text-slate-400">Rows Processed</dt>
                <dd className="text-base font-medium text-white">{result.rows_processed}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Students Created</dt>
                <dd className="text-base font-medium text-white">{result.students_created}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Students Updated</dt>
                <dd className="text-base font-medium text-white">{result.students_updated}</dd>
              </div>
              <div>
                <dt className="text-slate-400">Ingest Batch</dt>
                <dd className="font-mono text-white">{result.ingest_batch_id}</dd>
              </div>
            </dl>
            {result.errors.length > 0 && (
              <div className="mt-4 rounded border border-rose-700 bg-rose-900/30 p-3 text-rose-200">
                <p className="font-semibold">Errors</p>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  {result.errors.map((error) => (
                    <li key={error}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
