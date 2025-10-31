import './globals.css';
import type { Metadata } from 'next';

import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'CRDC PreCheck',
  description: 'Sprint 0 scaffold for CRDC readiness automation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
