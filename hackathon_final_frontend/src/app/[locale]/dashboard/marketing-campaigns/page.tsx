"use client";
import { useState, useEffect, useRef } from "react";
import { useTranslations } from "next-intl";

interface Campaign {
  _id: string;
  product_name: string;
  campaign_type: string;
  price: number;
  discount: string;
  poster_url: string | null;
  status: string;
  created_at: string;
}

interface CampaignResponse {
  status: string;
  campaigns: Campaign[];
}

const BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL;


export default function MarketingCampaignsPage() {
  const t = useTranslations();
  const tPage = useTranslations("marketingPage");
  const tAlerts = useTranslations("marketingAlerts");

  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const starsCanvas = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = starsCanvas.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const stars = Array.from({ length: 300 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      z: Math.random() * width,
    }));

    const drawStars = () => {
      ctx.fillStyle = "rgba(0,0,0,1)";
      ctx.fillRect(0, 0, width, height);
      for (let s of stars) {
        s.z -= 2;
        if (s.z <= 0) s.z = width;
        const k = 128.0 / s.z;
        const px = s.x * k + width / 2;
        const py = s.y * k + height / 2;
        if (px >= 0 && px <= width && py >= 0 && py <= height) {
          const size = (1 - s.z / width) * 2;
          const glow = ctx.createRadialGradient(px, py, 0, px, py, size * 6);
          glow.addColorStop(0, "rgba(0,255,255,1)");
          glow.addColorStop(0.5, "rgba(0,150,255,0.3)");
          glow.addColorStop(1, "transparent");
          ctx.beginPath();
          ctx.fillStyle = glow;
          ctx.arc(px, py, size, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      requestAnimationFrame(drawStars);
    };
    drawStars();

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    const fetchCampaigns = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${BASE_URL}/admin/marketing-campaigns`);
        const data: CampaignResponse = await res.json();
        if (data.status === "success") setCampaigns(data.campaigns);
        else setError(tAlerts("fetch_fail"));
      } catch (err) {
        console.error(err);
        setError(tAlerts("network_error"));
      } finally {
        setLoading(false);
      }
    };
    fetchCampaigns();
  }, [tAlerts]);

  if (loading)
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-black">
        <video autoPlay loop muted src="/loader.mp4" className="w-full h-full object-cover brightness-125" />
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/20 via-pink-400/20 to-purple-500/20 animate-gradient-x"></div>
        <div className="absolute text-cyan-300 text-xl font-bold">{tPage("loading")}</div>
      </div>
    );

  if (error)
    return (
      <div className="flex items-center justify-center min-h-screen text-red-500 text-xl">
        ❌ {error}
      </div>
    );

  return (
    <div className="flex min-h-screen relative overflow-x-hidden bg-black text-cyan-300">
      <canvas ref={starsCanvas} className="absolute inset-0 z-0 w-full h-full" />

      <main className="relative z-10 flex flex-wrap justify-center gap-6 p-4 sm:p-8 md:p-12">
        {campaigns.map((c) => (
          <div
            key={c._id}
            className="w-full sm:w-[calc(50%-1.5rem)] md:w-[calc(33.33%-2rem)] lg:w-[calc(25%-2rem)] 
                       p-6 bg-blue-950/40 border border-cyan-400/40 rounded-2xl 
                       shadow-[0_0_25px_rgba(0,255,255,0.4)] hover:shadow-[0_0_40px_rgba(0,255,255,0.8)] 
                       transition-all duration-300 backdrop-blur-xl"
          >
            <h3 className="text-xl font-semibold text-cyan-300 drop-shadow-[0_0_10px_#00ffff]">{c.product_name}</h3>
            <p className="text-sm text-gray-300">{tPage("type_label")}: {c.campaign_type}</p>
            <p className="text-lg font-bold text-green-400">{tPage("price_label")}: Rs. {c.price.toLocaleString()}</p>
            <p className="text-md font-bold text-pink-400">{c.discount}</p>
            <p className="text-sm opacity-60">{tPage("status_label")}: {c.status}</p>
            <p className="text-xs opacity-50 mt-2">{tPage("created_label")}: {new Date(c.created_at).toLocaleString()}</p>
          </div>
        ))}
      </main>

      <style>{`
        @keyframes gradient-x {
          0%,100% {background-position:0% 50%;}
          50% {background-position:100% 50%;}
        }
        .animate-gradient-x { background-size: 200% 200%; animation: gradient-x 5s ease infinite; }
      `}</style>
    </div>
  );
}
