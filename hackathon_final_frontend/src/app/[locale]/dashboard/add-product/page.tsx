"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { useTranslations, useLocale } from "next-intl";

export default function AddProduct() {
  const t = useTranslations("addProductPage");
  const tAlerts = useTranslations("alerts");
  const locale = useLocale();

  const [form, setForm] = useState({
    name: "",
    price: "",
    stock: "",
    category: "",
    stitching_type: "",
    color: "",
    description: "",
    image: null as File | null,
  });

  const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.name || !form.price || !form.image) {
      toast.error(tAlerts("required_fields"));
      return;
    }

    const formData = new FormData();
    Object.entries(form).forEach(([key, value]) => {
      if (value !== null) {
        if (key === "image" && value instanceof File) {
          formData.append(key, value);
        } else {
          formData.append(key, String(value));
        }
      }
    });

    try {
      setLoading(true);
      toast.loading(t("loading_upload"), { id: "upload" });

      const res = await fetch(`${BASE_URL}/products`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      toast.dismiss("upload");

      if (res.ok) {
        toast.success(tAlerts("upload_success"));
        setForm({
          name: "",
          price: "",
          stock: "",
          category: "",
          stitching_type: "",
          color: "",
          description: "",
          image: null,
        });
      } else {
        toast.error(`${data.detail || tAlerts("upload_fail")}`);
      }
    } catch {
      toast.dismiss("upload");
      toast.error(tAlerts("network_error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A0A0A] p-4 sm:p-6 md:p-10">
      <div className="relative w-full max-w-2xl md:max-w-3xl p-5 sm:p-8 rounded-2xl bg-gradient-to-br from-[#1A1A1A] via-[#111] to-[#000] shadow-[0_0_25px_#00ffff55] border border-cyan-500/30">

        <div className="absolute inset-0 rounded-2xl pointer-events-none border border-cyan-500/10 shadow-[0_0_20px_#00ffff44] animate-slowPulse"></div>

        <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-cyan-300 text-center drop-shadow-[0_0_10px_#00ffff] mb-3 sm:mb-4">
          {t("heading")}
        </h2>

        <p className="text-gray-400 text-center text-sm sm:text-base mb-6">
          {t("description")}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
          {/* Product Name */}
          <input
            className="w-full bg-gray-900/80 text-gray-100 border border-cyan-500/30 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 p-2.5 sm:p-3 rounded-md text-sm sm:text-base"
            placeholder={t("name_placeholder")}
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />

          {/* Price & Stock (Responsive grid) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <input
              type="number"
              className="w-full bg-gray-900/80 text-gray-100 border border-cyan-500/30 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 p-2.5 sm:p-3 rounded-md text-sm sm:text-base"
              placeholder={t("price_placeholder")}
              required
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
            />
            <input
              type="number"
              className="w-full bg-gray-900/80 text-gray-100 border border-cyan-500/30 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 p-2.5 sm:p-3 rounded-md text-sm sm:text-base"
              placeholder={t("stock_placeholder")}
              required
              value={form.stock}
              onChange={(e) => setForm({ ...form, stock: e.target.value })}
            />
          </div>

          {/* Category & Stitch Type */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="w-full bg-gray-900/80 text-gray-100 border border-cyan-500/30 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 p-2.5 sm:p-3 rounded-md text-sm sm:text-base"
            >
              <option value="">{t("category_placeholder")}</option>
              <option value="Women">Women</option>
              <option value="Men">Men</option>
              <option value="Kids">Kids</option>
            </select>

            <select
              value={form.stitching_type}
              onChange={(e) => setForm({ ...form, stitching_type: e.target.value })}
              className="w-full bg-gray-900/80 text-gray-100 border border-cyan-500/30 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 p-2.5 sm:p-3 rounded-md text-sm sm:text-base"
            >
              <option value="">{t("stitch_type_placeholder")}</option>
              <option value="Stitched">Stitched</option>
              <option value="Unstitched">Unstitched</option>
            </select>
          </div>

          {/* Color */}
          <input
            placeholder={t("color_placeholder")}
            value={form.color}
            onChange={(e) => setForm({ ...form, color: e.target.value })}
            className="w-full bg-gray-900/80 text-gray-100 border border-cyan-500/30 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 p-2.5 sm:p-3 rounded-md text-sm sm:text-base"
          />

          {/* Description */}
          <textarea
            rows={3}
            placeholder={t("description_placeholder")}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full bg-gray-900/80 text-gray-100 border border-cyan-500/30 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/40 p-2.5 sm:p-3 rounded-md text-sm sm:text-base"
          />

          {/* Image Upload */}
          <input
            type="file"
            required
            onChange={(e) => setForm({ ...form, image: e.target.files?.[0] || null })}
            className="w-full bg-gray-900 text-gray-300 border border-cyan-500/20 cursor-pointer file:bg-cyan-600 file:text-black file:px-4 file:py-2 file:rounded-lg text-sm sm:text-base"
          />

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2.5 sm:py-3 rounded-md text-black font-semibold text-base sm:text-lg transition shadow-lg glow-flicker ${
              loading ? "bg-gray-600 cursor-not-allowed" : "bg-cyan-400 hover:bg-cyan-300"
            }`}
          >
            {loading ? (
              <div className="flex items-center justify-center gap-3">
                <video autoPlay loop muted width="24" height="24" className="sm:w-7 sm:h-7">
                  <source src="/loader.mp4" type="video/mp4" />
                </video>
                {t("loading_upload")}
              </div>
            ) : (
              t("submit_button")
            )}
          </button>
        </form>
      </div>

      {/* Animations */}
      <style>{`
        .animate-slowPulse {
          animation: neonPulse 3s infinite alternate;
        }
        @keyframes neonPulse {
          0% { box-shadow: 0 0 10px #00ffff66; }
          100% { box-shadow: 0 0 30px #00ffffff; }
        }
        .glow-flicker {
          animation: flicker 2s infinite;
        }
        @keyframes flicker {
          0%, 100% { opacity: 1; }
          50% { opacity: .6; }
        }
      `}</style>
    </div>
  );
}
