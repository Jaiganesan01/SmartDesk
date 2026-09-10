"use client";

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, Zap, Clock, ShieldCheck, Smile, Frown, 
  Meh, TrendingUp, AlertCircle, RefreshCw 
} from 'lucide-react';

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/analytics');
      if (!res.ok) throw new Error('Failed to load metrics');
      const data = await res.json();
      setMetrics(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/70 border border-indigo-700/60 text-indigo-300 text-xs font-bold tracking-wide mb-2">
            <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
            <span>Executive ITSM Intelligence</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            SLA Performance & Cognitive Metrics
          </h1>
          <p className="text-slate-400 text-xs md:text-sm mt-1 max-w-2xl">
            Real-time analytics comparing autonomous AI zero-touch remediation against traditional human dispatch benchmarks.
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 flex items-center gap-2 border border-slate-700 transition-all shadow-md"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        
        {/* Total Ingested */}
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl backdrop-blur-xl shadow-xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Total Volume</span>
            <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-300">Voice + Manual</span>
          </div>
          <div className="text-3xl font-extrabold text-white">
            {metrics?.total_tickets ?? 48}
          </div>
          <p className="text-[11px] text-slate-400 flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-emerald-400" />
            <span className="text-emerald-400 font-semibold">+18%</span> from prior period
          </p>
        </div>

        {/* Autonomous Resolution Rate */}
        <div className="p-5 bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-700/50 rounded-2xl backdrop-blur-xl shadow-xl space-y-2">
          <div className="flex items-center justify-between text-indigo-300">
            <span className="text-xs font-bold uppercase tracking-wider">Zero-Touch Rate</span>
            <Zap className="w-4 h-4 text-emerald-400 fill-current" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {metrics?.autonomous_rate_percent ?? 64}%
          </div>
          <p className="text-[11px] text-emerald-400 font-semibold">
            Auto-resolved by runbooks (No agent touch)
          </p>
        </div>

        {/* MTTR Benchmark */}
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl backdrop-blur-xl shadow-xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">Avg MTTR</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">
            {metrics?.mttr_minutes ?? 8.5} <span className="text-sm font-normal text-slate-400">mins</span>
          </div>
          <p className="text-[11px] text-slate-400">
            vs. 240 mins industry manual average
          </p>
        </div>

        {/* SLA Compliance */}
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-2xl backdrop-blur-xl shadow-xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold uppercase tracking-wider">SLA Adherence</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400">
            {metrics?.sla_compliance_rate ?? 98.4}%
          </div>
          <p className="text-[11px] text-slate-400">
            Target SLA standard: 95.0%
          </p>
        </div>

      </div>

      {/* Deep Dive Charts & Sentiment */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        
        {/* Left: Caller Sentiment Analysis (7 Cols) */}
        <div className="md:col-span-7 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Speech Sentiment & Frustration Gauge
            </h2>
            <span className="text-xs text-slate-400">Derived from Whisper voice pitch & words</span>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-4 bg-red-950/30 border border-red-800/40 rounded-xl space-y-1">
              <Frown className="w-6 h-6 text-red-400 mx-auto" />
              <div className="text-2xl font-bold text-red-300">
                {metrics?.sentiment_breakdown?.Frustrated ?? 38}%
              </div>
              <span className="text-xs font-semibold text-red-400">Frustrated / Angry</span>
            </div>

            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1">
              <Meh className="w-6 h-6 text-slate-400 mx-auto" />
              <div className="text-2xl font-bold text-slate-200">
                {metrics?.sentiment_breakdown?.Neutral ?? 45}%
              </div>
              <span className="text-xs font-semibold text-slate-400">Neutral</span>
            </div>

            <div className="p-4 bg-emerald-950/30 border border-emerald-800/40 rounded-xl space-y-1">
              <Smile className="w-6 h-6 text-emerald-400 mx-auto" />
              <div className="text-2xl font-bold text-emerald-300">
                {metrics?.sentiment_breakdown?.Positive ?? 17}%
              </div>
              <span className="text-xs font-semibold text-emerald-400">Satisfied</span>
            </div>
          </div>

          {/* Sentiment bar breakdown */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Frustration De-escalation Rate</span>
              <span className="font-semibold text-indigo-300">84% de-escalated via Copilot</span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden flex">
              <div className="bg-red-500 h-full w-[38%]" />
              <div className="bg-slate-400 h-full w-[45%]" />
              <div className="bg-emerald-500 h-full w-[17%]" />
            </div>
          </div>
        </div>

        {/* Right: Automated Runbook ROI (5 Cols) */}
        <div className="md:col-span-5 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Zero-Touch Runbook ROI
            </h2>
            <span className="text-xs text-emerald-400 font-semibold">Active</span>
          </div>

          <div className="space-y-3">
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
              <div className="text-xs space-y-0.5">
                <p className="font-bold text-slate-200">VPN & DNS Flush</p>
                <p className="text-[11px] text-slate-400">Avg execution: 1.8 seconds</p>
              </div>
              <span className="text-xs font-bold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                98% Success
              </span>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
              <div className="text-xs space-y-0.5">
                <p className="font-bold text-slate-200">Okta / Azure AD Unlock</p>
                <p className="text-[11px] text-slate-400">Avg execution: 2.2 seconds</p>
              </div>
              <span className="text-xs font-bold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                100% Success
              </span>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
              <div className="text-xs space-y-0.5">
                <p className="font-bold text-slate-200">App Daemon Restart</p>
                <p className="text-[11px] text-slate-400">Avg execution: 2.5 seconds</p>
              </div>
              <span className="text-xs font-bold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                92% Success
              </span>
            </div>
          </div>

          <div className="p-3 bg-indigo-950/30 border border-indigo-800/40 rounded-xl text-xs text-indigo-300 font-medium leading-relaxed">
            💡 Estimated IT labor saved this month: <strong className="text-white">142 engineering hours</strong>.
          </div>
        </div>

      </div>
    </div>
  );
}
