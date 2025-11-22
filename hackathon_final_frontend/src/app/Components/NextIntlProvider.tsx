"use client";

import { NextIntlClientProvider } from 'next-intl';
import { ReactNode } from 'react';

export default function NextIntlProvider({
  children,
  locale,
  messages,
}: {
  children: ReactNode;
  locale: string;
  messages: any; // Ya proper type define karein
}) {
  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      {children}
    </NextIntlClientProvider>
  );
}