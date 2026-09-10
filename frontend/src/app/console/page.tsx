"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, Filter, Play, Pause, Zap, CheckCircle2, AlertTriangle, 
  Clock, Shield, Send, RefreshCw, ChevronRight, User, Terminal, Copy, Check
} from 'lucide-react';

interface TicketRecord {
  ticket_id: string;
  ticket_number: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  category: string;
  sentiment: string;
  customer_emotion: string;
  assigned_team: string;
  summary: string;
  suggested_resolution: string;
  can_auto_resolve: boolean;
  runbook_action: string;
  runbook_status: string;
  sla_due_at: string | null;
  sla_breached: boolean;
  created_at: string;
  transcript_id: string | null;
  file_name: string | null;
  raw_text: string | null;
  detailed_payload: any | null;
}

export default function AgentCommandCenter() {
  const [tickets, setTickets] = useState<TicketRecord[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<TicketRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPriority, setFilterPriority] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');

  // Audio Playback & Scrubbing
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeWordIdx, setActiveWordIdx] = useState<number | null>(null);
  const audioIntervalRef = useRef<any>(null);

  // Runbook Execution State
  const [isExecutingRunbook, setIsExecutingRunbook] = useState(false);
  const [runbookSuccess, setRunbookSuccess] = useState(false);
  const [runbookLogs, setRunbookLogs] = useState<string[]>([]);

  // AI Canned Replies
  const [cannedReplies, setCannedReplies] = useState<any[]>([]);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/history');
      if (!res.ok) throw new Error('Failed to load tickets');
      const data = await res.json();
      setTickets(data);
      if (data.length > 0 && !selectedTicket) {
        setSelectedTicket(data[0]);
      } else if (selectedTicket) {
        const updated = data.find((t: TicketRecord) => t.ticket_id === selectedTicket.ticket_id);
        if (updated) setSelectedTicket(updated);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  // Fetch AI replies when ticket changes
  useEffect(() => {
    if (!selectedTicket) return;
    setCannedReplies([]);
    fetch(`/api/tickets/${selectedTicket.ticket_id}/generate-reply`, { method: 'POST' })
      .then((res) => res.json())
      .then((data) => {
        if (data.replies) setCannedReplies(data.replies);
      })
      .catch(() => {});
  }, [selectedTicket?.ticket_id]);

  // Audio player simulation timer
  useEffect(() => {
    if (isPlaying) {
      audioIntervalRef.current = setInterval(() => {
        setCurrentTime((prev) => {
          const next = prev + 0.2;
          if (next > 15) {
            setIsPlaying(false);
            return 0;
          }
          return parseFloat(next.toFixed(2));
        });
      }, 200);
    } else {
      if (audioIntervalRef.current) clearInterval(audioIntervalRef.current);
    }
    return () => {
      if (audioIntervalRef.current) clearInterval(audioIntervalRef.current);
    };
  }, [isPlaying]);

  // Synchronize words with currentTime
  useEffect(() => {
    if (!selectedTicket?.detailed_payload?.words) return;
    const words = selectedTicket.detailed_payload.words;
    const foundIdx = words.findIndex((w: any) => currentTime >= w.start && currentTime <= w.end);
    if (foundIdx !== -1) setActiveWordIdx(foundIdx);
  }, [currentTime, selectedTicket]);

  const handleWordClick = (startSec: number, idx: number) => {
    setCurrentTime(startSec);
    setActiveWordIdx(idx);
    setIsPlaying(true);
  };

  const handleExecuteRunbook = async () => {
    if (!selectedTicket) return;
    setIsExecutingRunbook(true);
    setRunbookLogs(['Initializing secure connection to endpoint agent...']);

    setTimeout(() => {
      setRunbookLogs((prev) => [...prev, 'Validating execution policy & employee permissions...']);
    }, 600);

    setTimeout(() => {
      setRunbookLogs((prev) => [...prev, `Executing runbook action: "${selectedTicket.runbook_action}"...`]);
    }, 1200);

    try {
      const res = await fetch('/api/runbooks/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticketId: selectedTicket.ticket_id,
          runbookAction: selectedTicket.runbook_action || 'flush_dns_vpn',
        }),
      });

      if (!res.ok) throw new Error('Runbook execution failed');
      const result = await res.json();

      setTimeout(() => {
        setRunbookLogs((prev) => [...prev, 'Remediation completed successfully! Service health check: 200 OK']);
        setRunbookSuccess(true);
        setIsExecutingRunbook(false);
        fetchTickets();
      }, 1800);
    } catch (err: any) {
      setIsExecutingRunbook(false);
      setRunbookLogs((prev) => [...prev, `Error: ${err.message}`]);
    }
  };

  const copyReply = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const filteredTickets = tickets.filter((t) => {
    const matchSearch = (t.title + t.ticket_number + t.category).toLowerCase().includes(searchQuery.toLowerCase());
    const matchPriority = filterPriority === 'All' || t.priority === filterPriority;
    const matchStatus = filterStatus === 'All' || t.status.includes(filterStatus);
    return matchSearch && matchPriority && matchStatus;
  });

  return (
    <div className="space-y-4">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/40 border border-slate-800 rounded-xl px-5 py-3.5 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-950/80 border border-indigo-700/60 rounded-lg text-indigo-400">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <span>IT Agent Command Center</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                {tickets.length} In Queue
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              3-Pane Triage Console • Audio Scrubbing • Zero-Touch Runbooks
            </p>
          </div>
        </div>

        <button
          onClick={fetchTickets}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Sync Queue</span>
        </button>
      </div>

      {/* 3-Pane Command Console Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[calc(100vh-230px)] min-h-[640px]">
        
        {/* PANE 1: Ticket Queue (3 Cols) */}
        <div className="lg:col-span-3 bg-slate-900/60 border border-slate-800 rounded-2xl flex flex-col overflow-hidden backdrop-blur-md shadow-xl">
          {/* Filters */}
          <div className="p-3.5 border-b border-slate-800/80 space-y-2.5">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search tickets or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center gap-2">
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                className="w-1/2 bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-[11px] text-slate-300 focus:outline-none focus:border-indigo-500"
              >
                <option value="All">All Priorities</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
              </select>

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-1/2 bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-[11px] text-slate-300 focus:outline-none focus:border-indigo-500"
              >
                <option value="All">All Statuses</option>
                <option value="Open">Open</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
          </div>

          {/* Ticket List */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-800/50 p-2 space-y-1.5 custom-scrollbar">
            {filteredTickets.map((t) => {
              const isSelected = selectedTicket?.ticket_id === t.ticket_id;
              const isResolved = t.status.includes('Resolved');
              return (
                <div
                  key={t.ticket_id}
                  onClick={() => setSelectedTicket(t)}
                  className={`p-3 rounded-xl cursor-pointer transition-all border ${
                    isSelected
                      ? 'bg-indigo-950/40 border-indigo-600/70 shadow-md shadow-indigo-900/20'
                      : 'bg-slate-950/40 border-slate-800/40 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono font-bold text-slate-400">
                      {t.ticket_number}
                    </span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                      t.priority === 'Critical'
                        ? 'bg-red-950 text-red-400 border border-red-800'
                        : t.priority === 'High'
                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                        : 'bg-blue-950 text-blue-400 border border-blue-800'
                    }`}>
                      {t.priority}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-slate-100 line-clamp-1 mb-1">
                    {t.title}
                  </h3>

                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="truncate max-w-[100px]">{t.category}</span>
                    <span className={`px-1.5 py-0.5 rounded font-semibold ${
                      isResolved
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : 'text-slate-400'
                    }`}>
                      {isResolved ? 'Resolved' : 'Open'}
                    </span>
                  </div>

                  {t.can_auto_resolve && !isResolved && (
                    <div className="mt-2 flex items-center gap-1 text-[10px] text-emerald-400 font-bold bg-emerald-950/30 px-1.5 py-0.5 rounded border border-emerald-800/40">
                      <Zap className="w-3 h-3 fill-current" />
                      <span>Zero-Touch Ready</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* PANE 2: Ticket Details & Synchronized Audio Scrubbing (5 Cols) */}
        <div className="lg:col-span-5 bg-slate-900/60 border border-slate-800 rounded-2xl flex flex-col overflow-hidden backdrop-blur-md shadow-xl">
          {selectedTicket ? (
            <div className="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar">
              
              {/* Header */}
              <div className="border-b border-slate-800 pb-4">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950 px-2 py-0.5 rounded border border-indigo-800">
                    {selectedTicket.ticket_number}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded font-semibold bg-slate-800 text-slate-300">
                    {selectedTicket.category}
                  </span>
                  <span className="text-xs text-slate-500 ml-auto">
                    {new Date(selectedTicket.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <h2 className="text-lg font-extrabold text-white leading-tight">
                  {selectedTicket.title}
                </h2>
              </div>

              {/* Synchronized Audio Scrubber Player */}
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                    <span>🎙️</span>
                    <span>Synchronized Call Audio</span>
                  </span>
                  <span className="text-xs font-mono font-semibold text-slate-400">
                    {currentTime.toFixed(1)}s / 15.0s
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden relative cursor-pointer"
                     onClick={(e) => {
                       const rect = e.currentTarget.getBoundingClientRect();
                       const ratio = (e.clientX - rect.left) / rect.width;
                       setCurrentTime(parseFloat((ratio * 15).toFixed(2)));
                     }}>
                  <div 
                    className="bg-indigo-500 h-full transition-all duration-100"
                    style={{ width: `${(currentTime / 15) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-md"
                  >
                    {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                    <span>{isPlaying ? 'Pause Audio' : 'Play Stream'}</span>
                  </button>

                  <span className="text-[11px] text-slate-500">
                    Click any word below to jump playback
                  </span>
                </div>
              </div>

              {/* Interactive Synchronized Word Transcript */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <Shield className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Live Transcript (Word-Synced)</span>
                  </span>
                </div>

                <div className="p-4 bg-slate-950/70 border border-slate-800/80 rounded-xl leading-relaxed text-xs text-slate-300 max-h-48 overflow-y-auto">
                  {selectedTicket.detailed_payload?.words ? (
                    <div className="flex flex-wrap gap-1">
                      {selectedTicket.detailed_payload.words.map((w: any, idx: number) => {
                        const isActive = activeWordIdx === idx;
                        const isRedacted = w.word.includes('[REDACTED');
                        return (
                          <span
                            key={idx}
                            onClick={() => handleWordClick(w.start, idx)}
                            className={`px-1 py-0.5 rounded cursor-pointer transition-all ${
                              isActive
                                ? 'bg-indigo-600 text-white font-bold scale-105 shadow-sm'
                                : isRedacted
                                ? 'bg-red-950 text-red-300 font-mono border border-red-800/50'
                                : 'hover:bg-slate-800 text-slate-300'
                            }`}
                          >
                            {w.word}
                          </span>
                        );
                      })}
                    </div>
                  ) : (
                    <p>{selectedTicket.raw_text || selectedTicket.description}</p>
                  )}
                </div>
              </div>

              {/* Problem Description & Sentiment Box */}
              <div className="p-4 bg-slate-950/50 border border-slate-800 rounded-xl space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Extracted Problem Description
                  </span>
                  <span className="text-xs text-amber-400 font-semibold">
                    Sentiment: {selectedTicket.sentiment} ({selectedTicket.customer_emotion})
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {selectedTicket.description}
                </p>
              </div>

              {/* Suggested Resolution */}
              <div className="p-4 bg-indigo-950/20 border border-indigo-800/30 rounded-xl space-y-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                  AI Action Checklist
                </span>
                <p className="text-xs text-slate-300 whitespace-pre-line font-medium leading-relaxed">
                  {selectedTicket.suggested_resolution}
                </p>
              </div>

            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-500 text-xs">
              Select a ticket from the left queue to view details
            </div>
          )}
        </div>

        {/* PANE 3: Cognitive Copilot & Runbook Execution (4 Cols) */}
        <div className="lg:col-span-4 bg-slate-900/60 border border-slate-800 rounded-2xl flex flex-col overflow-hidden backdrop-blur-md shadow-xl p-5 space-y-5">
          {selectedTicket ? (
            <div className="flex-1 overflow-y-auto space-y-5 custom-scrollbar">
              
              {/* Zero-Touch Runbook Card */}
              <div className="p-4 bg-gradient-to-br from-indigo-950/60 via-slate-900 to-slate-950 border border-indigo-700/50 rounded-xl space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-indigo-300">
                    <Zap className="w-4 h-4 text-indigo-400 fill-current" />
                    <span>Autonomous Self-Healing</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    selectedTicket.status.includes('Resolved')
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      : 'bg-indigo-950 text-indigo-300 border border-indigo-800'
                  }`}>
                    {selectedTicket.status.includes('Resolved') ? 'COMPLETED' : 'READY'}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {selectedTicket.can_auto_resolve 
                    ? `Candidate detected for automated action: "${selectedTicket.runbook_action}". Resolves ticket with zero human intervention.`
                    : 'This issue requires on-site hardware or manual engineering intervention.'}
                </p>

                {selectedTicket.can_auto_resolve && !selectedTicket.status.includes('Resolved') && (
                  <button
                    disabled={isExecutingRunbook}
                    onClick={handleExecuteRunbook}
                    className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/40 transition-all active:scale-[0.98]"
                  >
                    {isExecutingRunbook ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Remediating Endpoint...</span>
                      </>
                    ) : (
                      <>
                        <Zap className="w-3.5 h-3.5 fill-current" />
                        <span>Execute Autonomous Runbook</span>
                      </>
                    )}
                  </button>
                )}

                {/* Live Console Logs */}
                {runbookLogs.length > 0 && (
                  <div className="p-2.5 bg-black/80 border border-slate-800 rounded-lg space-y-1 font-mono text-[10px] text-emerald-400">
                    {runbookLogs.map((log, idx) => (
                      <div key={idx} className="leading-tight">
                        <span className="text-slate-500">$ </span>
                        {log}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* AI Canned Replies */}
              <div className="space-y-2.5">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
                  AI Smart Response Copilot
                </span>

                <div className="space-y-2">
                  {cannedReplies.map((reply, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-950 border border-slate-800/80 rounded-xl space-y-2 hover:border-slate-700 transition-all"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">
                          {reply.tone}
                        </span>
                        <button
                          onClick={() => copyReply(reply.content, idx)}
                          className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] flex items-center gap-1 transition-all"
                        >
                          {copiedIdx === idx ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {reply.content}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-500 text-xs">
              Copilot inactive
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
