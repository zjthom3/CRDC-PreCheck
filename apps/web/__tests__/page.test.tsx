import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import HomePage from '../app/page';
import { Providers } from '../app/providers';

describe('HomePage', () => {
  beforeEach(() => {
    vi.spyOn(global, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();

      if (url.endsWith('/districts')) {
        return new Response(
          JSON.stringify([
            { id: '11111111-1111-1111-1111-111111111111', name: 'Demo', timezone: 'America/Chicago' },
          ]),
          { status: 200 },
        );
      }

      if (url.includes('/rules/runs')) {
        return new Response(JSON.stringify([]), { status: 200 });
      }

      if (url.includes('/rules/results')) {
        return new Response(JSON.stringify([]), { status: 200 });
      }

      if (url.includes('/readiness')) {
        return new Response(JSON.stringify({ items: [] }), { status: 200 });
      }

      if (url.includes('/admin/health')) {
        return new Response(JSON.stringify({ connectors: [], last_validation: null }), { status: 200 });
      }

      throw new Error(`Unhandled fetch call: ${url}`);
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders heading and action button', async () => {
    render(
      <Providers>
        <HomePage />
      </Providers>,
    );

    await waitFor(() => expect(screen.getByText('CRDC PreCheck')).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /run validation/i })).toBeInTheDocument();
  });
});
