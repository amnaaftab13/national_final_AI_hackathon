"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import toast from "react-hot-toast";

interface PurchaseTransaction {
  _id: string;
  product_name: string;
  quantity_purchased: number;
  amount_paid: number;
  supplier_name: string;
  purchased_at?: string;
}

interface PurchaseReport {
  report_type: "supplier_purchases";
  status: string;
  total_records: number;
  total_spent: number;
  message?: string;
  data: PurchaseTransaction[];
}

const BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL;


export default function PurchaseReportPage() {
  const tPage = useTranslations("purchaseReportPage");
  const tAlerts = useTranslations("purchaseAlerts");

  const [report, setReport] = useState<PurchaseReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await fetch(`${BASE_URL}/admin/purchase-report`);
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
        <div className="absolute text-cyan-300 text-xl sm:text-2xl font-bold">
          {tPage("loading")}
        </div>
      </div>
    );
  }

  if (error || !report?.data) {
    return (
      <div className="flex items-center justify-center min-h-screen text-red-500 text-xl sm:text-2xl">
         {error || tPage("no_purchases")}
      </div>
    );
  }

  const { total_records, total_spent, data: purchases } = report;

  return (
    <div className="min-h-screen bg-[#030303] p-4 sm:p-6 md:p-8 lg:p-12 overflow-y-auto text-cyan-300 relative">
      <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-center mb-8 md:mb-10 drop-shadow-[0_0_22px_#00ffff]">
        {tPage("heading")}
      </h1>

      {/* Summary Card */}
      <div className="neon-card relative bg-gradient-to-r from-cyan-900 to-black p-4 sm:p-6 md:p-8 rounded-xl mb-8 sm:mb-10 border border-cyan-500 shadow-[0_0_25px_#00eaffaa] max-w-full">
        <p className="text-xl sm:text-2xl md:text-3xl font-bold">
          {tPage("total_records_label")}: {total_records}
        </p>
        <p className="text-xl sm:text-2xl md:text-3xl font-bold mt-3">
          {tPage("total_spent_label")}: Rs. {total_spent?.toLocaleString() ?? 0}
        </p>
      </div>

      {/* Purchase Records */}
      {purchases.length > 0 ? (
        purchases.map((item, idx) => (
          <div
            key={idx}
            className="group neon-card relative bg-black/70 border border-cyan-400/40 p-4 sm:p-6 md:p-8 rounded-xl
              shadow-[0_0_18px_#00fff2aa] hover:shadow-[0_0_45px_#00fff2ff]
              transition duration-500 mb-6 sm:mb-8 overflow-hidden max-w-full"
          >
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold mb-3 sm:mb-4">📦 {item.product_name}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-5">
              <div className="bg-cyan-900/30 p-3 sm:p-4 rounded-lg border border-cyan-500/30 text-center">
                <p className="text-sm sm:text-base opacity-70">{tPage("quantity_label")}</p>
                <p className="text-lg sm:text-xl font-bold">{item.quantity_purchased}</p>
              </div>
              <div className="bg-cyan-900/30 p-3 sm:p-4 rounded-lg border border-cyan-500/30 text-center">
                <p className="text-sm sm:text-base opacity-70">{tPage("amount_paid_label")}</p>
                <p className="text-lg sm:text-xl font-bold">
                  Rs. {item.amount_paid.toLocaleString()}
                </p>
              </div>
              <div className="bg-cyan-900/30 p-3 sm:p-4 rounded-lg border border-cyan-500/30 text-center">
                <p className="text-sm sm:text-base opacity-70">{tPage("supplier_label")}</p>
                <p className="text-lg sm:text-xl font-bold">{item.supplier_name}</p>
              </div>
            </div>
            <p className="text-sm sm:text-base opacity-60">
              {tPage("purchased_on_label")}: {item.purchased_at?.split("T")?.[0] ?? "N/A"}
            </p>
          </div>
        ))
      ) : (
        <p className="text-center text-sm sm:text-base opacity-70">{tPage("no_purchases")}</p>
      )}

      <style>{`
        @keyframes bgPulse {
          0% { opacity: 0.12; transform: scale(1); }
          100% { opacity: 0.28; transform: scale(1.07); }
        }
        .animate-bgPulse {
          animation: bgPulse 5s infinite alternate;
        }

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
