import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Insta Follow Manager",
  description: "Dashboard analitico e triagem alfabetica de Seguindo e Seguidores no Instagram",
};

const THEME_INIT_SCRIPT = `(function(){try{var s=localStorage.getItem("theme");var d=window.matchMedia("(prefers-color-scheme: dark)").matches;if(s==="dark"||(s!=="light"&&d)){document.documentElement.classList.add("dark");}else{document.documentElement.classList.remove("dark");}}catch(e){}})();`;

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="pt-BR"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-full flex flex-col bg-[var(--background)] text-[var(--foreground)] transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}
