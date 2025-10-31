import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import LoginPage from '../app/login/page';
import { Providers } from '../app/providers';

describe('LoginPage', () => {
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

  it('renders SSO form', async () => {
    render(
      <Providers>
        <LoginPage />
      </Providers>,
    );

    expect(await screen.findByText('Single Sign-On')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
  });
});
