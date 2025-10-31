import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import ImportPage from '../app/import/page';
import { Providers } from '../app/providers';

describe('ImportPage', () => {
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

      throw new Error(`Unhandled fetch call: ${url}`);
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders mapping fields and upload control', async () => {
    render(
      <Providers>
        <ImportPage />
      </Providers>,
    );

    expect(await screen.findByText('Import Students from CSV')).toBeInTheDocument();
    expect(screen.getByLabelText(/CSV File/i)).toBeInTheDocument();
    expect(screen.getByText('Start Import')).toBeDisabled();
  });
});
