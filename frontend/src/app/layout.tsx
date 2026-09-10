import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "SmartDesk AI | Cognitive ITSM & Autonomous Ingestion",
  description: "Enterprise AI-driven audio transcription, autonomous runbooks, and ITSM control console.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased min-h-screen flex flex-col font-sans selection:bg-indigo-500 selection:text-white bg-slate-950 text-slate-100">
        
        {/* Top Enterprise Navigation Header */}
        <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 via-indigo-600 to-emerald-500 flex items-center justify-center text-white font-extrabold text-lg shadow-lg shadow-indigo-500/25">
                ⚡
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                    SmartDesk<span className="text-indigo-400">.AI</span>
                  </span>
                  <span className="px-2 py-0.5 text-[9px] font-black tracking-widest uppercase bg-indigo-950/80 text-indigo-400 border border-indigo-700/60 rounded-full shadow-inner">
                    COGNITIVE ITSM
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 -mt-0.5 font-medium tracking-tight">
                  Autonomous Triage & Multimodal Audio Ingestion
                </p>
              </div>
            </div>
            
            {/* Nav Menu */}
            <nav className="flex items-center gap-1.5 md:gap-2">
              <Link
                href="/"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/70 transition-all flex items-center gap-1.5"
              >
                <span>🎙️</span>
                <span>Voice Studio</span>
              </Link>
              <Link
                href="/console"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/70 transition-all flex items-center gap-1.5"
              >
                <span>⚡</span>
                <span>Command Center</span>
              </Link>
              <Link
                href="/incidents"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/70 transition-all flex items-center gap-1.5"
              >
                <span>📡</span>
                <span>Outage Radar</span>
              </Link>
              <Link
                href="/analytics"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/70 transition-all flex items-center gap-1.5"
              >
                <span>📊</span>
                <span>Analytics & SLA</span>
              </Link>
              <Link
                href="/history"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/70 transition-all flex items-center gap-1.5"
              >
                <span>🗃️</span>
                <span>Archive</span>
              </Link>
              <Link
                href="/tickets"
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-all flex items-center gap-1.5"
              >
                <span>✏️</span>
                <span>Manual</span>
              </Link>
            </nav>

            {/* Status Pulse */}
            <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-emerald-950/40 border border-emerald-800/50 rounded-full">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]" />
              <span className="text-[11px] font-semibold text-emerald-300">
                AI Pipeline: Online
              </span>
            </div>
          </div>
        </header>

        {/* Page Content Container */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-6 py-8">
          {children}
        </main>

        {/* Enterprise Footer */}
        <footer className="border-t border-slate-900/80 bg-slate-950/50 py-6 text-center text-xs text-slate-500 flex flex-col md:flex-row items-center justify-between max-w-7xl mx-auto px-6 w-full gap-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-400">SmartDesk AI Platform</span>
            <span>•</span>
            <span>ITIL v4 & SOC2 Type II Certified Pipeline</span>
          </div>
          <div className="flex items-center gap-4 text-slate-500">
            <span>LLaMA-3.1 + Whisper-large-v3</span>
            <span>•</span>
            <span>Zero-Touch Autonomous Remediation</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
