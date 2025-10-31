import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import ExceptionsPage from '../app/exceptions/page';
import { Providers } from '../app/providers';

describe('ExceptionsPage', () => {
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

      if (url.endsWith('/exceptions')) {
        return new Response(JSON.stringify([]), { status: 200 });
      }

      throw new Error(`Unhandled fetch call: ${url}`);
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders page shell', async () => {
    render(
      <Providers>
        <ExceptionsPage />
      </Providers>,
    );

    expect(await screen.findByText('Exceptions')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Packet/ })).toBeDisabled();
  });
});
