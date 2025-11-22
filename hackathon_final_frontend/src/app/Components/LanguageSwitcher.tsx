'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useLocale } from 'next-intl';
import { useMemo } from 'react';

export default function LanguageSwitcher() {
  const pathname = usePathname();
  const locale = useLocale(); // ✅ gives 'en' or 'ur'

  // ✅ Replace only the locale part of the path
  const englishPath = useMemo(() => pathname.replace(/^\/(ur|en)/, '/en'), [pathname]);
  const urduPath = useMemo(() => pathname.replace(/^\/(ur|en)/, '/ur'), [pathname]);

  const activeLanguage = locale === 'ur' ? 'ur' : 'en';

  return (
    <div
      className="relative inline-flex items-center gap-1 sm:gap-2 bg-gradient-to-r 
                 from-black/80 via-gray-900/80 to-black/80 
                 backdrop-blur-md border border-cyan-400/40 rounded-full p-1 sm:p-1.5
                 shadow-[0_0_20px_rgba(0,255,255,0.3)] sm:shadow-[0_0_25px_rgba(0,255,255,0.3)]
                 transition-all duration-300 text-xs sm:text-sm"
    >
      {/* Sliding Blue Indicator */}
      <div
        className={`absolute top-0 left-0
                    w-1/2 h-full
                    bg-gradient-to-r from-blue-600/80 to-cyan-500/80
                    border border-cyan-400/80 rounded-full 
                    shadow-[0_0_25px_rgba(0,255,255,0.8),inset_0_0_15px_rgba(0,255,255,0.6)]
                    transition-all duration-500 ease-in-out z-5
                     `}
      />

      {/* English Button */}
      <Link
        href={englishPath}
        className={`relative z-10 flex items-center justify-center px-3 sm:px-6 py-1.5 sm:py-2.5 
                    rounded-full font-bold text-sm tracking-wide text-center
                    transition-all duration-300 w-1/2
                    ${
                      activeLanguage === 'en'
                        ? 'bg-gradient-to-r from-blue-600/30 to-cyan-500/30 text-white border border-cyan-400/50 drop-shadow-[0_0_12px_rgba(0,255,255,1)] sm:drop-shadow-[0_0_15px_rgba(0,255,255,1)] shadow-inner'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }`}
      >
        English
      </Link>

      {/* Urdu Button */}
      <Link
        href={urduPath}
        className={`relative z-10 flex items-center justify-center px-3 sm:px-6 py-1.5 sm:py-2.5 
                    rounded-full font-bold text-sm tracking-wide text-center
                    transition-all duration-300 w-1/2
                    ${
                      activeLanguage === 'ur'
                        ? 'bg-gradient-to-r from-blue-600/30 to-cyan-500/30 text-white border border-cyan-400/50 drop-shadow-[0_0_12px_rgba(0,255,255,1)] sm:drop-shadow-[0_0_15px_rgba(0,255,255,1)] shadow-inner'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }`}
      >
        اردو
      </Link>
    </div>
  );
}
