"use client";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import toast from "react-hot-toast";

interface Product {
  name: string;
  price: number;
  stock: number;
  category?: string;
  stitching_type?: string;
  color?: string;
  description?: string;
  image_url?: string;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;


export default function ViewProducts() {
  const tPage = useTranslations("viewProductsPage");
  const tAlerts = useTranslations("viewAlerts");

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${BASE_URL}/products`);
        const data = await res.json();
        console.log(data);
        if (data.success && Array.isArray(data.data)) {
          setProducts(data.data);
        } else {
          throw new Error("Invalid response");
        }
      } catch (err) {
        console.error(err);
        setError(tAlerts("network_error"));
        toast.error(tAlerts("network_error"));
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [tAlerts]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black flex flex-col justify-center items-center z-50 overflow-hidden">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover opacity-70"
          src="/loader.mp4"
        />
        <div className="relative z-10 text-cyan-300 text-2xl md:text-3xl lg:text-4xl font-bold drop-shadow-[0_0_15px_#00ffff] animate-pulse">
          {tPage("loading")}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen text-red-500 text-xl text-center p-4">
        {error}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#030303] px-4 sm:px-6 lg:px-12 py-10 relative overflow-hidden">
      
      <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(0,255,255,0.08)_0%,transparent_70%)] animate-bgPulse"></div>

      <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-cyan-300 text-center drop-shadow-[0_0_12px_#00ffff] mb-10">
        {tPage("heading")}
      </h2>

      {products.length === 0 ? (
        <p className="text-gray-400 text-center text-lg">{tPage("no_products")}</p>
      ) : (
        <div
          className="grid gap-6 sm:gap-8 place-items-center
          grid-cols-[repeat(auto-fit,minmax(220px,1fr))]"
        >
          {products.map((p, i) => (
            <div
              key={i}
              className="relative w-full bg-gradient-to-br from-[#111] to-[#000]
              border border-cyan-400/40 rounded-xl p-4 sm:p-5
              shadow-[0_0_25px_#00eaff66] hover:shadow-[0_0_55px_#00eaffcc]
              backdrop-blur-sm transition-all duration-500
              hover:-translate-y-2 group overflow-hidden"
            >
              {/* ⭐ FULL IMAGE – NO CROP */}
              <div className="relative w-full max-h-80 rounded-lg overflow-hidden flex items-center justify-center bg-black">
                <img
                  src={p.image_url || "/placeholder.png"}
                  alt={p.name}
                  className="max-h-80 w-auto object-contain transition duration-700 group-hover:scale-105"
                />
              </div>

              <h3 className="text-lg sm:text-xl font-semibold text-cyan-300 mt-3">
                {p.name}
              </h3>
              <p className="text-gray-400 text-sm sm:text-base">
                {p.category || tPage("unknown_category")} •{" "}
                {p.stitching_type || "N/A"}
              </p>
              <p className="font-bold text-cyan-300 mt-1 text-sm sm:text-base">
                {tPage("price_label")}: Rs. {p.price}
              </p>
              <p className="text-xs sm:text-sm text-gray-500">
                {tPage("stock_label")}: {p.stock}
              </p>
            </div>
          ))}
        </div>
      )}

      <style>{`
        @keyframes bgPulse {
          0% { opacity: 0.2; transform: scale(1); }
          100% { opacity: 0.4; transform: scale(1.05); }
        }
        .animate-bgPulse {
          animation: bgPulse 4s infinite alternate ease-in-out;
        }
      `}</style>
    </div>
  );
}
