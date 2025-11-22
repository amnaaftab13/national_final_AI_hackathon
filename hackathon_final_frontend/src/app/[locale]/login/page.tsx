"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff } from "lucide-react";
import { Toaster, toast } from "react-hot-toast";
import LanguageSwitcher from "@/app/Components/LanguageSwitcher";
import { useTranslations, useLocale } from "next-intl";

export default function LoginPage() {
  const t = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const toastId = "login-toast";
  const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

  const handleLogin = () => {
    if (loading) return;
    if (!email || !password) {
      toast.dismiss(toastId);
      toast.error(t("login_failed_alert"), { id: toastId });
      return;
    }

    setLoading(true);

    const LOGIN_ENDPOINT = `${BASE_URL}/api/admins/login`;

    fetch(LOGIN_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    })
      .then((res) => {
        if (!res.ok) {
          return res.text().then((text) => {
            throw new Error(`${t("network_error_alert")}: ${text}`);
          });
        }
        return res.json();
      })
      .then((data) => {
        if (data.success) {
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("admin_info", JSON.stringify(data.admin_info));

          toast.dismiss(toastId);
          toast.success(t("login_button") + " " + t("login_heading"), {
            id: toastId,
            duration: 1500,
          });

          setTimeout(() => {
            toast.dismiss();
            router.push(`/${locale}/dashboard`);
          }, 1500);
        } else {
          const errorMsg = data.message || data.detail || t("login_failed_alert");
          toast.dismiss(toastId);
          toast.error(` ${errorMsg}`, { id: toastId });

          setLoading(false); 
        }
      })
      .catch((err) => {
        toast.dismiss(toastId);
        toast.error(`💥 ${err.message}`, { id: toastId });

        setLoading(false); 
      });
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 sm:p-6 md:p-8">
      {/* Toast Notifications */}
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 3000,
          style: {
            background: "#1a1a1a",
            color: "#fff",
            border: "1px solid #22d3ee",
          },
          success: { iconTheme: { primary: "#22d3ee", secondary: "#fff" } },
          error: { iconTheme: { primary: "#ef4444", secondary: "#fff" } },
        }}
      />

      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        src="/loader.mp4"
        className="absolute inset-0 w-full h-full object-cover brightness-110"
      />
      <div className="absolute inset-0 bg-black/30"></div>

      {/* Login Card */}
      <div className="relative z-10 bg-black/70 backdrop-blur-md 
           p-5 sm:p-6 md:p-8 
           rounded-2xl shadow-xl 
           max-w-xs sm:max-w-sm md:max-w-md 
           flex flex-col gap-4 border border-cyan-400/30">

        {/* Language Switcher */}
        <div className="flex justify-center mb-3 sm:mb-4">
          <LanguageSwitcher />
        </div>

        {/* Title */}
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-cyan-300 text-center mb-4 sm:mb-6 drop-shadow-[0_0_10px_#00ffff]">
          {t("login_heading")}
        </h1>

        {/* Email Input */}
        <input
          type="email"
          placeholder={t("email_placeholder")}
          value={email}
          autoComplete="email"
          onChange={(e) => setEmail(e.target.value)}
          className={`w-full p-2.5 sm:p-3 rounded-lg border border-cyan-400/30 bg-black/50 text-white placeholder-cyan-300 focus:ring-2 focus:ring-cyan-400 focus:outline-none transition
      ${locale === "ur" ? "text-right" : "text-left"}`}
          required
        />

        {/* Password Input */}
        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            placeholder={t("password_placeholder")}
            value={password}
            autoComplete="current-password"
            onChange={(e) => setPassword(e.target.value)}
            className={`w-full p-2.5 sm:p-3 pr-10 rounded-lg border border-cyan-400/30 bg-black/50 text-white placeholder-cyan-300 focus:ring-2 focus:ring-cyan-400 focus:outline-none transition
       ${locale === "ur" ? "text-right" : "text-left"}`}
            required
          />
          <div
            className={`absolute top-1/2 -translate-y-1/2 cursor-pointer 
       ${locale === "ur" ? "left-3" : "right-3"}`}
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? (
              <EyeOff className="w-5 h-5 sm:w-6 sm:h-6 text-cyan-400" />
            ) : (
              <Eye className="w-5 h-5 sm:w-6 sm:h-6 text-cyan-400" />
            )}
          </div>
        </div>

        {/* Login Button */}
        <button
          type="button"
          disabled={loading}
          onClick={handleLogin}
          className="w-full py-2.5 sm:py-3 md:py-3.5 
          bg-cyan-500 text-black font-bold 
          text-sm sm:text-base md:text-lg 
          rounded-lg hover:bg-cyan-400 transition-all duration-300 
          shadow-lg hover:shadow-cyan-500/50 
          flex items-center justify-center gap-2 
          disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading && (
            <span className="w-4 h-4 sm:w-5 sm:h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          )}
          {loading ? t("logging_in") : t("login_button")}
        </button>

        <p className="text-[10px] sm:text-xs md:text-sm text-gray-400 text-center mt-2">
          &copy; 2025 {t("copyright_text")}
        </p>
      </div>
    </div>
  );
}