"use client";
import { useRouter } from "next/navigation";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import Image from "next/image";

export default function MainPage({ locale }: { locale: string }) {
  const router = useRouter();
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const handleMouseMove = (e: React.MouseEvent) => {
    const { clientX, clientY } = e;
    const { innerWidth, innerHeight } = window;
    mouseX.set((clientX - innerWidth / 2) / innerWidth);
    mouseY.set((clientY - innerHeight / 2) / innerHeight);
  };

  const images = [
    "/fashion1.jpg",
    "/fashion2.jpg",
    "/fashion3.jpg",
    "/fashion4.jpg",
    "/fashion5.jpg",
  ];

  const x = useSpring(mouseX, { stiffness: 40, damping: 20 });
  const y = useSpring(mouseY, { stiffness: 40, damping: 20 });
  const rotateX = useTransform(y, [-0.5, 0.5], [-15, 15]);
  const rotateY = useTransform(x, [-0.5, 0.5], [-15, 15]);

  const LOGIN_PATH = "login";
  const handleLoginClick = () => {
    const finalLocale = locale || "en";
    const targetPath = `/${finalLocale}/${LOGIN_PATH}`;
    router.push(targetPath);
  };

  return (
    <div
      className="relative min-h-screen flex flex-col items-center justify-center text-center text-white bg-[#030b14] overflow-hidden"
      onMouseMove={handleMouseMove}
    >
      {/* 🎥 Background Video */}
      <video
        className="absolute inset-0 w-full h-full object-cover z-0"
        autoPlay
        muted
        loop
        playsInline
      >
        <source src="/agentic_bg.mp4" type="video/mp4" />
      </video>

      {/* Gradient Lights */}
      <motion.div
        className="absolute inset-0 z-10"
        style={{
          x: useTransform(x, [-0.5, 0.5], [-40, 40]),
          y: useTransform(y, [-0.5, 0.5], [-25, 25]),
        }}
      >
        <div className="absolute top-10 left-10 w-[200px] h-[200px] sm:w-[250px] sm:h-[250px] md:w-[350px] md:h-[350px] bg-gradient-to-br from-cyan-400/20 via-blue-500/20 to-purple-600/20 rounded-full blur-[80px]" />
        <div className="absolute bottom-10 right-10 w-[250px] h-[250px] sm:w-[320px] sm:h-[320px] md:w-[400px] md:h-[400px] bg-gradient-to-tr from-purple-500/20 via-pink-400/20 to-cyan-400/20 rounded-full blur-[90px]" />
      </motion.div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="relative z-20 font-black text-4xl sm:text-5xl md:text-6xl lg:text-7xl tracking-tight leading-tight bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent drop-shadow-[0_0_35px_rgba(0,255,255,0.5)] px-4"
      >
        AI Fashion Bazar
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.7 }}
        className="text-base sm:text-lg md:text-2xl text-gray-300 font-light mt-3 z-20 px-4"
      >
        آپ کا ذوق اے آئی کا زور
      </motion.p>

      {/* Carousel */}
      <motion.div
        className="relative z-20 mt-10 w-full overflow-hidden"
        style={{ rotateX, rotateY, transformPerspective: 1000 }}
      >
        <div className="flex animate-scroll gap-4 sm:gap-6 md:gap-8 lg:gap-10 py-6 sm:py-8 px-3 sm:px-6 md:px-10">
          {images.concat(images).map((src, idx) => (
            <motion.div
              key={idx}
              className="flex-shrink-0 w-[120px] h-[120px] sm:w-[150px] sm:h-[150px] md:w-[180px] md:h-[180px] lg:w-[200px] lg:h-[200px] relative rounded-full border border-cyan-400/30 shadow-[0_0_25px_rgba(0,255,255,0.5)] overflow-hidden"
              whileHover={{ scale: 1.1 }}
            >
              <Image
                src={src}
                alt={`Fashion ${idx + 1}`}
                fill
                className="object-cover rounded-full hover:brightness-110 transition-all"
              />
            </motion.div>
          ))}
        </div>
      </motion.div>


      {/* CTA Button */}
      <motion.button
        onClick={handleLoginClick}
        className="
    mt-8 z-20
    px-5 py-2.5 
    sm:px-6 sm:py-3 
    md:px-8 md:py-3.5 
    lg:px-10 lg:py-4
    text-sm sm:text-base md:text-lg 
    font-semibold text-black 
    bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500
    rounded-full shadow-[0_0_25px_rgba(0,255,255,0.5)]
    hover:scale-105 transition-all duration-300
  "
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.95 }}
      >
        Enter the AI Dashboard
      </motion.button>

      <style jsx>{`
        .animate-scroll {
          animation: scroll 25s linear infinite;
        }
        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
      `}</style>

      {/* HUD Info */}
      <motion.div
        className="absolute bottom-3 left-4 sm:bottom-5 sm:left-6 text-[10px] sm:text-xs text-cyan-400/60 font-mono"
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.7 }}
        transition={{ delay: 1.5, duration: 1 }}
      >
        <div>Neural Sync: 100%</div>
        <div>Style Engine: Online</div>
      </motion.div>
    </div>
  );
}
