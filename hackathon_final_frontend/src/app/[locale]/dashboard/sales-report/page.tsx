"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import toast from "react-hot-toast";

interface ProductSoldData {
  name: string;
  quantity: number;
  price: number;
  total: number;
}

interface Transaction {
  order_id: string;
  total_sales_amount: number;
  products_sold: ProductSoldData[];
  payment_method: string;
  paid_at: string;
}

interface ReportData {
  total_orders: number;
  total_revenue: number;
  transactions: Transaction[];
  product_summary: Record<string, { total_quantity: number; total_sales: number }>;
}

interface SalesReport {
  status: string;
  message?: string;
  data: ReportData;
}

const BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL;

export default function SalesReportPage() {
  const tPage = useTranslations("salesReportPage");
  const tAlerts = useTranslations("salesAlerts");

  const [report, setReport] = useState<SalesReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchReport() {
      try {
        const res = await fetch(`${BASE_URL}/admin/sales-report`);
        const data = await res.json();

        const parsed =
          typeof data.report === "string" ? JSON.parse(data.report) : data.report;

        const formattedData = {
          ...parsed.data,
          product_summary: Object.fromEntries(
            Object.entries(parsed.data.product_summary).map(([key, item]: any) => [
              key,
              {
                total_quantity: item.quantity,
                total_sales: item.revenue,
              },
            ])
          ),
        };

        setReport({ ...parsed, data: formattedData });
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
        <div className="absolute text-cyan-300 text-xl sm:text-2xl font-bold">{tPage("loading")}</div>
      </div>
    );
  }

  if (error || !report?.data) {
    return (
      <div className="flex items-center justify-center min-h-screen text-red-500 text-xl sm:text-2xl">
         {error || "No Data Found!"}
      </div>
    );
  }

  const { total_orders, total_revenue, transactions, product_summary } = report.data;

  return (
    <div className="min-h-screen bg-[#030303] p-4 sm:p-6 md:p-8 lg:p-12 overflow-y-auto text-cyan-300 relative">
      <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-center mb-8 md:mb-10 drop-shadow-[0_0_22px_#00ffff]">
        {tPage("heading")}
      </h1>

      {/* Summary Cards */}
      <div className="neon-card relative bg-gradient-to-r from-cyan-900 to-black p-4 sm:p-6 md:p-8 rounded-xl mb-8 sm:mb-10 border border-cyan-500 shadow-[0_0_25px_#00eaffaa] max-w-full">
        <p className="text-xl sm:text-2xl md:text-3xl font-bold">{tPage("total_orders_label")}: {total_orders}</p>
        <p className="text-xl sm:text-2xl md:text-3xl font-bold mt-3">{tPage("total_revenue_label")}: Rs. {total_revenue?.toLocaleString?.() ?? 0}</p>
      </div>

      {/* Orders Section */}
      {transactions.length > 0 ? (
        transactions.map((order, index) => (
          <div
            key={index}
            className="group neon-card relative bg-black/70 border border-cyan-400/40 p-4 sm:p-6 md:p-8 rounded-xl
              shadow-[0_0_18px_#00fff2aa] hover:shadow-[0_0_45px_#00fff2ff]
              transition duration-500 mb-6 sm:mb-8 overflow-hidden max-w-full"
          >
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold mb-3 sm:mb-4">🧾 Order: {order.order_id}</h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-5">
              <div className="bg-cyan-900/30 p-3 sm:p-4 rounded-lg border border-cyan-500/30 text-center">
                <p className="text-sm sm:text-base opacity-70">{tPage("total_sales_label")}</p>
                <p className="text-lg sm:text-xl font-bold">Rs. {order.total_sales_amount.toLocaleString()}</p>
              </div>
              <div className="bg-cyan-900/30 p-3 sm:p-4 rounded-lg border border-cyan-500/30 text-center">
                <p className="text-sm sm:text-base opacity-70">{tPage("payment_method_label")}</p>
                <p className="text-lg sm:text-xl font-bold">{order.payment_method}</p>
              </div>
              <div className="bg-cyan-900/30 p-3 sm:p-4 rounded-lg border border-cyan-500/30 text-center">
                <p className="text-sm sm:text-base opacity-70">{tPage("paid_on_label")}</p>
                <p className="text-lg sm:text-xl font-bold">{order.paid_at?.split?.(" ")?.[0] ?? ""}</p>
              </div>
            </div>

            <h3 className="text-lg sm:text-xl md:text-2xl font-semibold mt-4 mb-3">{tPage("products_label")}</h3>
            <div className="space-y-2 sm:space-y-3">
              {order.products_sold.map((item, idx) => (
                <div
                  key={idx}
                  className="flex flex-col sm:flex-row justify-between bg-cyan-950/40 p-3 rounded-md border border-cyan-600/30"
                >
                  <span className="font-bold">{item.name}</span>
                  <span>Qty: {item.quantity}</span>
                  <span>Rs. {item.total}</span>
                </div>
              ))}
            </div>
          </div>
        ))
      ) : (
        <p className="text-center text-sm sm:text-base opacity-70">{tPage("no_orders")}</p>
      )}

      {/* Product Summary Table */}
      {!!Object.keys(product_summary).length && (
        <div className="overflow-x-auto bg-black/70 rounded-xl border border-cyan-500 p-4 sm:p-6 md:p-8 mt-6 sm:mt-8 md:mt-10">
          <h2 className="text-xl sm:text-2xl md:text-3xl font-bold mb-4">{tPage("product_summary_label")}</h2>
          <table className="w-full table-auto border-collapse min-w-[400px] sm:min-w-[600px] md:min-w-full">
            <thead>
              <tr className="border-b border-cyan-600">
                <th className="pb-1 text-left text-sm sm:text-base">{tPage("product_column")}</th>
                <th className="pb-1 text-right text-sm sm:text-base">{tPage("quantity_column")}</th>
                <th className="pb-1 text-right text-sm sm:text-base">{tPage("sales_column")}</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(product_summary).map(([name, stats], idx) => (
                <tr key={idx} className="border-b border-cyan-900/60">
                  <td className="py-2 font-semibold text-left text-sm sm:text-base">{name}</td>
                  <td className="py-2 text-right text-sm sm:text-base">{stats.total_quantity ?? 0}</td>
                  <td className="py-2 text-right text-sm sm:text-base">Rs. {(stats.total_sales ?? 0).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Neon / Lightning Animation */}
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
