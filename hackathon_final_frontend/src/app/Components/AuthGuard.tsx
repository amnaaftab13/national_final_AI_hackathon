"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthGuard({
  children, 
  locale,
}: {
  children: React.ReactNode; 
  locale: string;
}) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      const finalLocale = locale || "en";
      
      router.replace(`/${finalLocale}/login`);
    } else {
      setAuthorized(true);
    }
  }, [router, locale]);

  if (!authorized) {
    return (
      <div className="h-screen flex items-center justify-center bg-black text-cyan-500">
        <span className="animate-pulse text-xl font-bold">Loading...</span>
      </div>
    );
  }

  return <>{children}</>;
}