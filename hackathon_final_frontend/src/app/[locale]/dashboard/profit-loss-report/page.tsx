"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import toast from "react-hot-toast";

interface ProfitLossData {
  total_sales: number;
  total_purchases: number;
  profit_loss: number;
}

interface ProfitLossReport {
  report_type: string;
  status: string;
  message: string;
  data: ProfitLossData;
}

const BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL;


export default function ProfitLossPage() {
  const tPage = useTranslations("profitLossPage");
  const tAlerts = useTranslations("profitLossAlerts");

  const [report, setReport] = useState<ProfitLossReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await fetch(`${BASE_URL}/admin/profit-loss-report`);
        const data = await res.json();
        const parsed =
          typeof data.report === "string" ? JSON.parse(data.report) : data.report;
        setReport(parsed);
      } catch (err) {
        console.error(err);
        setError(tAlerts("network_error"));
        toast.error(tAlerts("network_error"));
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [tAlerts]);

  if (loading) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center overflow-hidden bg-black">
        <video
          autoPlay
          loop
          muted
          src="/loader.mp4"
          className="absolute inset-0 w-full h-full object-cover brightness-110"
        />
        <div className="absolute text-cyan-300 text-xl font-bold">
          {tPage("loading")}
        </div>
      </div>
    );
  }

  if (error || !report?.data) {
    return (
      <div className="flex items-center justify-center min-h-screen text-red-500 text-xl">
        ❌ {error || "No Data Found!"}
      </div>
    );
  }

  const { total_sales, total_purchases, profit_loss } = report.data;
  const isProfitable = profit_loss >= 0;

  return (
    <div className="min-h-screen bg-[#030303] p-4 sm:p-6 md:p-8 lg:p-12 overflow-y-auto text-cyan-300 relative">
      <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-center mb-8 md:mb-10 drop-shadow-[0_0_22px_#00ffff]">
        {tPage("heading")}
      </h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6 mb-8 md:mb-10">
        <div className="neon-card relative bg-black/70 border border-cyan-500 p-4 sm:p-6 rounded-xl shadow-[0_0_25px_#00eaffaa] text-center">
          <p className="text-sm sm:text-base opacity-70">{tPage("total_sales_label")}</p>
          <p className="text-2xl sm:text-3xl font-bold text-green-400">
            Rs. {total_sales.toLocaleString()}
          </p>
        </div>

        <div className="neon-card relative bg-black/70 border border-cyan-500 p-4 sm:p-6 rounded-xl shadow-[0_0_25px_#00eaffaa] text-center">
          <p className="text-sm sm:text-base opacity-70">{tPage("total_purchases_label")}</p>
          <p className="text-2xl sm:text-3xl font-bold text-orange-400">
            Rs. {total_purchases.toLocaleString()}
          </p>
        </div>

        <div
          className={`neon-card relative bg-black/70 border-l-4 p-4 sm:p-6 rounded-xl shadow-[0_0_25px_#00eaffaa] text-center ${
            isProfitable ? "border-green-400" : "border-red-500"
          }`}
        >
          <p className="text-sm sm:text-base opacity-70">
            {isProfitable ? tPage("net_profit_label") : tPage("net_loss_label")}
          </p>
          <p className={`text-2xl sm:text-3xl font-bold ${isProfitable ? "text-green-400" : "text-red-500"}`}>
            Rs. {Math.abs(profit_loss).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Financial Summary */}
      <div className="neon-card relative bg-black/70 border border-cyan-500 p-4 sm:p-6 md:p-8 rounded-xl shadow-[0_0_25px_#00eaffaa] max-w-full">
        <h2 className="text-2xl sm:text-3xl font-bold mb-4 drop-shadow-[0_0_22px_#00ffff] text-cyan-300">
          {tPage("financial_summary_label")}
        </h2>
        <div className="bg-cyan-900/20 p-3 sm:p-4 rounded-md mb-4 overflow-x-auto">
          {report.message.split("\n").map((line, idx) => (
            <p key={idx} className="text-sm sm:text-base opacity-80">
              {line}
            </p>
          ))}
        </div>

        {/* Sales vs Purchases */}
        <div className="mb-4">
          <div className="flex justify-between mb-1 text-sm sm:text-base opacity-70">
            <span>{tPage("sales_vs_purchases_label")}</span>
            <span>
              {((total_sales / (total_sales + total_purchases)) * 100).toFixed(1)}%
              Sales
            </span>
          </div>
          <div className="w-full h-4 sm:h-5 bg-cyan-900/30 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-400 transition-all duration-500"
              style={{
                width: `${(total_sales / (total_sales + total_purchases)) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Profit Margin */}
        <div className="mt-4 p-3 sm:p-4 bg-cyan-900/20 rounded-md flex justify-between items-center">
          <span className="opacity-70">{tPage("profit_margin_label")}</span>
          <span className="font-bold text-base sm:text-lg">
            {total_sales > 0 ? ((profit_loss / total_sales) * 100).toFixed(2) : 0}%
          </span>
        </div>
      </div>

      {/* Neon card hover effect */}
      <style>{`
        .neon-card::before {
          content: "";
          position: absolute;
          top: -120%;
          left: 0;
          width: 100%;
          height: 250%;
          background: linear-gradient(
            115deg,
            transparent 40%,
            rgba(255, 255, 255, 0.25) 50%,
            transparent 60%
          );
          transform: translateX(-100%);
          transition: 0.8s;
        }
        .neon-card:hover::before {
          transform: translateX(100%);
        }
      `}</style>
    </div>
  );
}
