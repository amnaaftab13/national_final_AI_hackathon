"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface Admin {
  name: string;
  email: string;
  image_url?: string;
  role: string;
}

interface UserContextType {
  admin: Admin | null;
  setAdmin: (admin: Admin) => void;
}

const UserContext = createContext<UserContextType>({
  admin: null,
  setAdmin: () => {},
});

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [admin, setAdmin] = useState<Admin | null>(null);

  useEffect(() => {
    const info = localStorage.getItem("admin_info");
    if (info) setAdmin(JSON.parse(info));
  }, []);

  return <UserContext.Provider value={{ admin, setAdmin }}>{children}</UserContext.Provider>;
};

export const useAdmin = () => useContext(UserContext);
