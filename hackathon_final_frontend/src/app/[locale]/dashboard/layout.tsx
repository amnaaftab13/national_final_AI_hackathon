'use client';
import React, { useEffect, useState } from 'react';
import Sidebar from '@/app/Components/Sidebar';
import LanguageSwitcher from '@/app/Components/LanguageSwitcher';
import AuthGuard from '@/app/Components/AuthGuard';

interface Admin {
  name: string;
  image_url?: string;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [admin, setAdmin] = useState<Admin | null>(null);

  useEffect(() => {
    const info = localStorage.getItem('admin_info');
    if (info) setAdmin(JSON.parse(info));
  }, []);

  return (
    <AuthGuard locale="en">
    <div className="flex min-h-screen bg-black">
      <Sidebar admin={admin} />
      
      <div className="flex-1 flex flex-col">
        {/* Top Bar with Language Switcher */}
        <div className="flex justify-end p-4 bg-gradient-to-r from-black via-gray-900 to-black border-b border-cyan-500/20">
          <LanguageSwitcher />
        </div>
        
        {/* Main Content */}
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
    </AuthGuard>
  );
}