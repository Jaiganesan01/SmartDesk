"use client";

import React, { useState, useEffect } from 'react';
import { 
  Radio, AlertTriangle, ShieldAlert, Users, Bell, RefreshCw, 
  CheckCircle2, ArrowRight, Zap, ExternalLink, Send
} from 'lucide-react';
import Link from 'next/link';

interface Cluster {
  id: string;
  category: string;
  ticket_count: number;
  severity: string;
  primary_symptom: string;
  tickets: Array<{ id: string; number: string; title: string; priority: string }>;
  suggested_action: string;
}

export default function IncidentsRadar() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [outagesDetected, setOutagesDetected] = useState(0);
  
  // Broadcast modal state
  const [broadcastTitle, setBroadcastTitle] = useState('');
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [broadcastStatus, setBroadcastStatus] = useState<'idle' | 'sending' | 'sent'>('idle');

  const fetchClusters = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/incidents/clusters');
      if (!res.ok) throw new Error('Failed to fetch incident clusters');
      const data = await res.json();
      setClusters(data.clusters || []);
      setOutagesDetected(data.outages_detected || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, []);

  const handleBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!broadcastTitle || !broadcastMessage) return;

    setBroadcastStatus('sending');
    try {
      const res = await fetch('/api/incidents/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: broadcastTitle,
          message: broadcastMessage,
          severity: 'Critical',
        }),
      });
      if (!res.ok) throw new Error('Broadcast failed');
      setBroadcastStatus('sent');
      setTimeout(() => {
        setBroadcastStatus('idle');
        setBroadcastTitle('');
        setBroadcastMessage('');
      }, 2500);
    } catch (err) {
      setBroadcastStatus('idle');
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-950/70 border border-red-800/60 text-red-300 text-xs font-bold tracking-wide mb-2">
            <Radio className="w-3.5 h-3.5 text-red-400 animate-pulse" />
            <span>Real-Time Semantic Outage Radar</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Major Incident & Anomaly Detection
          </h1>
          <p className="text-slate-400 text-xs md:text-sm mt-1 max-w-2xl">
            Correlates incoming voice transcripts to identify widespread outages before human triage teams notice the pattern.
          </p>
        </div>

        <button
          onClick={fetchClusters}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 flex items-center gap-2 border border-slate-700 transition-all shadow-md"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Scan Outage Radar</span>
        </button>
      </div>

      {/* Outage Banner Alert */}
      {outagesDetected > 0 ? (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-red-950/80 via-slate-900 to-amber-950/40 border border-red-700/60 flex items-center justify-between shadow-2xl animate-pulse">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-900/60 rounded-xl text-red-300 border border-red-700">
              <ShieldAlert className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Major Outage Cluster Active ({outagesDetected} Impacted Service Areas)
              </h3>
              <p className="text-xs text-red-200 mt-0.5">
                High ticket velocity detected within a 30-minute window. Automated incident response recommended.
              </p>
            </div>
          </div>

          <a
            href="#broadcast-section"
            className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold shadow-lg shadow-red-900/40 transition-all"
          >
            Dispatch Company Alert
          </a>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 flex items-center gap-3 text-emerald-300 text-xs font-medium">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>All monitored systems operating within nominal baseline ticket velocity.</span>
        </div>
      )}

      {/* Clusters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clusters.map((cluster) => {
          const isCritical = cluster.severity.includes('Critical');
          const isWarning = cluster.severity.includes('Warning');
          return (
            <div
              key={cluster.id}
              className={`p-6 rounded-2xl bg-slate-900/60 border backdrop-blur-xl shadow-xl flex flex-col justify-between transition-all hover:scale-[1.01] ${
                isCritical
                  ? 'border-red-600/70 shadow-red-950/20'
                  : isWarning
                  ? 'border-amber-600/70 shadow-amber-950/20'
                  : 'border-slate-800'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    {cluster.category}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    isCritical
                      ? 'bg-red-950 text-red-400 border border-red-800'
                      : isWarning
                      ? 'bg-amber-950 text-amber-400 border border-amber-800'
                      : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  }`}>
                    {cluster.severity}
                  </span>
                </div>

                <h3 className="text-base font-extrabold text-white leading-snug">
                  {cluster.primary_symptom}
                </h3>

                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1 font-semibold text-slate-200">
                    <Users className="w-3.5 h-3.5 text-indigo-400" />
                    {cluster.ticket_count} Correlated Calls
                  </span>
                  <span>•</span>
                  <span>Velocity: Elevated</span>
                </div>

                {/* Linked Tickets */}
                <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                    Correlated Tickets
                  </span>
                  <div className="space-y-1">
                    {cluster.tickets.map((t) => (
                      <div
                        key={t.id}
                        className="flex items-center justify-between text-[11px] bg-slate-950/70 px-2.5 py-1.5 rounded-lg border border-slate-800 text-slate-300"
                      >
                        <span className="font-mono text-indigo-400 font-bold">{t.number}</span>
                        <span className="truncate max-w-[140px] text-slate-300">{t.title}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action recommendation */}
              <div className="mt-5 pt-3 border-t border-slate-800">
                <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                  <span className="font-semibold text-slate-200">Recommendation:</span> {cluster.suggested_action}
                </p>
                <Link
                  href="/console"
                  className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all border border-slate-700"
                >
                  <span>Triage in Console</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* Broadcast Emergency Advisory Form */}
      <div id="broadcast-section" className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 backdrop-blur-xl shadow-2xl space-y-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-amber-950/60 border border-amber-800/60 rounded-xl text-amber-400">
            <Bell className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-extrabold text-white">
              Dispatch Organization-Wide Incident Advisory
            </h2>
            <p className="text-xs text-slate-400">
              Pushes emergency banner updates to Slack, MS Teams, and Employee Self-Service portals.
            </p>
          </div>
        </div>

        <form onSubmit={handleBroadcast} className="space-y-4 max-w-2xl">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
              Incident Headline
            </label>
            <input
              type="text"
              placeholder="e.g. Investigating GlobalProtect VPN Gateway Interruption"
              value={broadcastTitle}
              onChange={(e) => setBroadcastTitle(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
              Employee Instructions & Remediation Status
            </label>
            <textarea
              rows={3}
              placeholder="Our network engineering team is aware of connection drops following the patch. Workaround: avoid disconnecting active sessions..."
              value={broadcastMessage}
              onChange={(e) => setBroadcastMessage(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={broadcastStatus === 'sending'}
            className="px-6 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-amber-900/30 transition-all"
          >
            {broadcastStatus === 'sending' ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Publishing Broadcast...</span>
              </>
            ) : broadcastStatus === 'sent' ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                <span>Advisory Dispatched!</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Publish Advisory to All Channels</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
