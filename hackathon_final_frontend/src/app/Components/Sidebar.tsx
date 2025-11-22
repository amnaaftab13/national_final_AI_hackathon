"use client";
import { useState } from "react";
import Link from "next/link";
import { useTranslations, useLocale } from "next-intl";

interface Admin {
  name: string;
  image_url?: string;
  brand_name?: string;
}

interface SidebarProps {
  admin: Admin | null;
}

export default function Sidebar({ admin }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const t = useTranslations("sidebar");
  const locale = useLocale();

  const navItems = [
    { label: t("dashboard"), href: `/${locale}/dashboard`, icon: "📊" },
    { label: t("addProduct"), href: `/${locale}/dashboard/add-product`, icon: "➕" },
    { label: t("viewProducts"), href: `/${locale}/dashboard/view-products`, icon: "📦" },
    { label: t("salesReport"), href: `/${locale}/dashboard/sales-report`, icon: "💰" },
    { label: t("purchaseReport"), href: `/${locale}/dashboard/purchase-report`, icon: "🛒" },
    { label: t("profitLoss"), href: `/${locale}/dashboard/profit-loss-report`, icon: "📉" },
    { label: t("marketing"), href: `/${locale}/dashboard/marketing-campaigns`, icon: "📣" },
    { label: t("logs"), href: `/${locale}/dashboard/logs`, icon: "📜" },
  ];

  return (
    <>
      {/* Hamburger */}
      <div className={`md:hidden fixed top-4 z-30 ${locale === "ur" ? "right-4" : "left-4"}`}>
        <button
          onClick={() => setMobileOpen(true)}
          className="relative w-9 h-9 flex flex-col justify-center items-center gap-[4px] 
            bg-[#020617]/80 border border-cyan-500/40 rounded-xl 
            shadow-[0_0_12px_#00ffff] hover:shadow-[0_0_18px_#00ffffaa] 
            transition-all active:scale-95"
        >
          <span className="w-5 h-[2px] bg-cyan-300 rounded-full"></span>
          <span className="w-5 h-[2px] bg-cyan-300 rounded-full"></span>
          <span className="w-5 h-[2px] bg-cyan-300 rounded-full"></span>
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`fixed md:static top-0 z-40 p-4 md:p-5 min-h-screen transition-all duration-300
          ${collapsed ? "md:w-20" : "md:w-64"}
          ${mobileOpen 
            ? "translate-x-0" 
            : locale === "ur" 
              ? "translate-x-full md:translate-x-0" 
              : "-translate-x-full md:translate-x-0"
          }
          ${locale === "ur" 
            ? "right-0 md:right-auto md:left-auto" 
            : "left-0"
          }
          bg-[#020617] border-r border-cyan-500/40 shadow-[0_0_35px_#00eaff99] backdrop-blur-xl 
          w-72 sm:w-64
        `}
      >

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <span className="text-3xl neon-pulse">🛍</span>
              <h1 className="text-lg  font-bold text-cyan-300 drop-shadow-[0_0_12px_#00ffff]">
                {t("brand_name")}
              </h1>
            </div>
          )}

          <button
            className="text-cyan-300 text-lg hover:text-white p-1 transition transform active:scale-90 hidden md:block"
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? "➡️" : "⬅️"}
          </button>

          <button
            className="md:hidden text-cyan-300 text-2xl hover:text-white"
            onClick={() => setMobileOpen(false)}
          >
            ✖
          </button>
        </div>

        {/* Admin Info */}
        {!collapsed && (
          <div className="flex items-center gap-3 mb-6 p-3 sm:p-4 rounded-lg 
            border border-cyan-500/40 bg-cyan-500/10 
            shadow-[0_0_15px_#00aaff60]"
          >
            {admin ? (
              <>
                <img
                  src={admin.image_url || "/default-avatar.png"}
                  alt={admin.name}
                  className="w-10 h-10 sm:w-12 sm:h-12 rounded-full object-cover border border-cyan-400 shadow-[0_0_10px_#00ffff]"
                />
                <div>
                  <p className="text-cyan-300 font-semibold text-sm sm:text-base">
                    {admin.name}
                  </p>
                  <span className="text-gray-400 text-xs">{t("admin")}</span>
                </div>
              </>
            ) : (
              <span className="text-gray-400">{t("loading")}</span>
            )}
          </div>
        )}

        {/* Navigation */}
        <nav className="flex flex-col space-y-1 sm:space-y-2">
          {navItems.map((item, idx) => (
            <Link
              key={idx}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={`group flex items-center gap-3 px-3 py-2 sm:py-3 rounded-lg text-gray-200 hover:text-white 
                transition-all overflow-hidden ${
                  collapsed ? "justify-center" : "justify-start"
                } 
                hover:bg-gradient-to-r hover:from-cyan-500/30 hover:to-blue-500/20 
                border border-transparent hover:border-cyan-500/50 
                shadow-[0_0_12px_#00eaff30] hover:shadow-[0_0_22px_#00eaff70]`}
            >
              <span className="text-xl sm:text-2xl drop-shadow-[0_0_6px_#00ffff]">
                {item.icon}
              </span>
              {!collapsed && (
                <span className="text-sm sm:text-base tracking-wide">
                  {item.label}
                </span>
              )}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 md:hidden transition-opacity"
          onClick={() => setMobileOpen(false)}
        />
      )}
    </>
  );
}
