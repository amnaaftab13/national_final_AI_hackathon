import { notFound } from 'next/navigation';
import enCommon from '../locales/en/common.json';
import urCommon from '../locales/ur/common.json';
import { Toaster } from "react-hot-toast";
import { UserProvider } from "./dashboard/context/UserContext";
import NextIntlProvider from '@/app/Components/NextIntlProvider';

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'ur' }];
}

export default async function LocaleLayout({ 
  children, 
  params 
}: { 
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  let messages;
  if (locale === 'en') messages = enCommon;
  else if (locale === 'ur') messages = urCommon;
  else return notFound();

  return (
    <html lang={locale} dir={locale === 'ur' ? 'rtl' : 'ltr'}>
      <body className="antialiased">
        <UserProvider>
          <NextIntlProvider locale={locale} messages={messages}>
            {children}
          </NextIntlProvider>
          <Toaster position="top-center" reverseOrder={false} />
        </UserProvider>
      </body>
    </html>
  );
}