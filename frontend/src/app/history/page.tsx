"use client";

import React, { useEffect, useState } from 'react';
import { Archive, Search, Filter, Edit3, Trash2, Calendar, FileText, ChevronDown, ChevronUp, RefreshCw, X } from 'lucide-react';

interface TicketRecord {
  ticket_id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  category: string;
  ticket_date: string;
  transcript_id: string | null;
  file_name: string | null;
  raw_text: string | null;
  transcript_status: string | null;
  detailed_payload: any | null;
}

export default function HistoryDashboard() {
  const [records, setRecords] = useState<TicketRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filtering states
  const [search, setSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [categoryFilter, setCategoryFilter] = useState('All');
  
  // Expanded tickets
  const [expandedId, setExpandedId] = useState<string | null>(null);
  
  // Edit Modal/Panel State
  const [editingTicket, setEditingTicket] = useState<TicketRecord | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editPriority, setEditPriority] = useState('Medium');
  const [editCategory, setEditCategory] = useState('Software');
  const [editStatus, setEditStatus] = useState('Open');
  const [updateStatus, setUpdateStatus] = useState<'idle' | 'updating' | 'error' | 'success'>('idle');

  // Deletion confirm state
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('/api/history');
      if (!response.ok) {
        throw new Error('Failed to load transaction history.');
      }
      const data = await response.json();
      setRecords(data);
    } catch (err: any) {
      setError(err.message || 'Could not fetch records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleUpdateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTicket) return;

    setUpdateStatus('updating');
    try {
      const response = await fetch(`/api/tickets/${editingTicket.ticket_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: editTitle,
          description: editDescription,
          priority: editPriority,
          category: editCategory,
          status: editStatus
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update ticket.');
      }

      setUpdateStatus('success');
      setTimeout(() => {
        setEditingTicket(null);
        setUpdateStatus('idle');
        fetchHistory();
      }, 1000);
    } catch (err: any) {
      setUpdateStatus('error');
    }
  };

  const handleDeleteTicket = async (ticketId: string) => {
    try {
      const response = await fetch(`/api/tickets/${ticketId}`, {
        method: 'DELETE'
      });
      if (!response.ok) {
        throw new Error('Failed to delete ticket.');
      }
      setDeletingId(null);
      fetchHistory();
    } catch (err: any) {
      alert(err.message || 'Error deleting ticket.');
    }
  };

  const openEditPanel = (ticket: TicketRecord) => {
    setEditingTicket(ticket);
    setEditTitle(ticket.title);
    setEditDescription(ticket.description);
    setEditPriority(ticket.priority);
    setEditCategory(ticket.category);
    setEditStatus(ticket.status);
  };

  // Filter records
  const filteredRecords = records.filter(r => {
    const matchesSearch = r.title.toLowerCase().includes(search.toLowerCase()) || 
                          r.ticket_id.toLowerCase().includes(search.toLowerCase()) ||
                          (r.file_name && r.file_name.toLowerCase().includes(search.toLowerCase()));
    
    const matchesPriority = priorityFilter === 'All' || r.priority === priorityFilter;
    const matchesCategory = categoryFilter === 'All' || r.category === categoryFilter;

    return matchesSearch && matchesPriority && matchesCategory;
  });

  return (
    <div className="space-y-6 relative">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-950/60 border border-indigo-800 rounded-lg text-indigo-400">
            <Archive className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
              Ticket Command Queue
            </h1>
            <p className="text-slate-400 text-xs mt-0.5">
              Browse audio logs, verify transcripts, and update dispatch specifications.
            </p>
          </div>
        </div>

        <button 
          onClick={fetchHistory}
          className="p-2 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 transition-colors text-slate-300 flex items-center gap-2 text-xs font-semibold"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Queue
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl grid grid-cols-1 md:grid-cols-3 gap-4 backdrop-blur-sm">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
          <input
            type="text"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 text-xs"
            placeholder="Search by Title, ID, or Audio File..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex gap-2">
          <span className="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-500 shrink-0">
            <Filter className="w-4 h-4" />
          </span>
          <select
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-300 focus:outline-none text-xs cursor-pointer"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="All">All Priorities</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>

        <select
          className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-300 focus:outline-none text-xs cursor-pointer"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="All">All Categories</option>
          <option value="Software">Software</option>
          <option value="Hardware">Hardware</option>
          <option value="Authentication">Authentication</option>
          <option value="Billing">Billing</option>
        </select>
      </div>

      {/* Main List */}
      {loading ? (
        <div className="py-20 text-center text-slate-500 flex flex-col items-center justify-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          <span className="text-xs">Loading queue history...</span>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-950/20 border border-red-900/50 rounded-xl text-center text-red-400 text-sm">
          {error}
        </div>
      ) : filteredRecords.length === 0 ? (
        <div className="py-20 bg-slate-950/20 border border-slate-900 rounded-xl text-center text-slate-500 text-xs">
          No tickets matching filters found in the database.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredRecords.map((r) => {
            const isExpanded = expandedId === r.ticket_id;
            const pColors: any = {
              High: 'bg-red-500/10 text-red-400 border-red-500/20',
              Medium: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
              Low: 'bg-green-500/10 text-green-400 border-green-500/20'
            };
            const priorityBadge = pColors[r.priority] || 'bg-slate-800 text-slate-400';

            return (
              <div 
                key={r.ticket_id} 
                className={`border rounded-xl bg-slate-900/20 backdrop-blur-sm transition-colors ${
                  isExpanded ? 'border-indigo-500/50 bg-slate-900/30' : 'border-slate-850 hover:border-slate-800'
                }`}
              >
                {/* List Summary Row */}
                <div 
                  onClick={() => setExpandedId(isExpanded ? null : r.ticket_id)}
                  className="p-5 flex items-center justify-between cursor-pointer select-none"
                >
                  <div className="flex-1 pr-6">
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="text-[10px] font-bold font-mono text-slate-500">
                        {r.ticket_id.split('-')[0].toUpperCase() || 'MANUAL'}
                      </span>
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${priorityBadge}`}>
                        {r.priority}
                      </span>
                      <span className="px-2 py-0.5 text-[10px] font-bold rounded border border-slate-800 bg-slate-950 text-slate-400">
                        {r.category}
                      </span>
                      <span className="px-2 py-0.5 text-[10px] font-bold rounded border border-indigo-950 bg-indigo-950/30 text-indigo-400">
                        {r.status}
                      </span>
                    </div>

                    <h3 className="font-bold text-sm text-slate-100 mt-2 hover:text-indigo-400 transition-colors">
                      {r.title}
                    </h3>
                    
                    <p className="text-slate-400 text-xs mt-1 max-w-2xl truncate">
                      {r.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-6 text-slate-500 shrink-0">
                    <div className="text-right text-xs">
                      <div className="font-semibold text-slate-400 flex items-center gap-1.5 justify-end">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        {new Date(r.ticket_date).toLocaleDateString()}
                      </div>
                      <div className="text-[10px] text-slate-600 mt-0.5">
                        {r.file_name ? `🎙️ ${r.file_name}` : '✏️ Manual'}
                      </div>
                    </div>
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t border-slate-850 p-6 bg-slate-950/30 space-y-5">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-3">
                        <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                          Customer Issue Description
                        </h4>
                        <div className="p-4 bg-slate-950 rounded-xl border border-slate-900 text-xs text-slate-300 leading-relaxed">
                          {r.description}
                        </div>
                      </div>

                      <div className="space-y-3">
                        <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                          🎙️ Associated Transcript Data
                        </h4>
                        {r.raw_text ? (
                          <div className="p-4 bg-slate-950 rounded-xl border border-slate-900 space-y-3 text-xs">
                            <p className="italic text-indigo-300">"{r.raw_text}"</p>
                            <div className="h-px bg-slate-900 my-2"></div>
                            <div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500">
                              <div>File: <code className="text-slate-400">{r.file_name}</code></div>
                              <div>Duration: <code className="text-slate-400">{r.detailed_payload?.duration || '12.5'}s</code></div>
                            </div>
                          </div>
                        ) : (
                          <div className="p-4 bg-slate-950 rounded-xl border border-slate-900 text-xs text-slate-500 italic">
                            No voice recordings are linked to this manual ticket.
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center justify-between border-t border-slate-850 pt-4 mt-4">
                      <div className="flex items-center gap-3">
                        <button 
                          onClick={() => openEditPanel(r)}
                          className="px-3.5 py-2 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-300 hover:bg-slate-800 transition-colors flex items-center gap-1.5 font-bold"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                          Edit Details
                        </button>

                        {deletingId === r.ticket_id ? (
                          <div className="flex items-center gap-2 bg-red-950/20 border border-red-900/50 px-3 py-1.5 rounded-lg text-xs">
                            <span className="text-red-400 font-semibold">Delete permanently?</span>
                            <button 
                              onClick={() => handleDeleteTicket(r.ticket_id)}
                              className="text-red-300 hover:text-red-200 font-bold ml-1"
                            >
                              Yes
                            </button>
                            <span className="text-slate-700">|</span>
                            <button 
                              onClick={() => setDeletingId(null)}
                              className="text-slate-400 hover:text-slate-300"
                            >
                              No
                            </button>
                          </div>
                        ) : (
                          <button 
                            onClick={() => setDeletingId(r.ticket_id)}
                            className="px-3.5 py-2 text-xs bg-red-950/15 border border-red-950/40 rounded-lg text-red-400 hover:bg-red-950/30 transition-colors flex items-center gap-1.5 font-bold"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            Delete Ticket
                          </button>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-600">DB UUID: {r.ticket_id}</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Editing Drawer Panel (Overlay) */}
      {editingTicket && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full p-6 flex flex-col justify-between shadow-2xl text-slate-100">
            <div>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <Edit3 className="w-4 h-4 text-indigo-400" />
                  <h2 className="text-lg font-bold">Edit Ticket Parameters</h2>
                </div>
                <button 
                  onClick={() => setEditingTicket(null)}
                  className="p-1 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleUpdateTicket} className="space-y-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Title
                  </label>
                  <input
                    type="text"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500 text-xs"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Description
                  </label>
                  <textarea
                    rows={4}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-slate-200 focus:outline-none focus:border-indigo-500 text-xs"
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Priority
                  </label>
                  <select
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none text-xs"
                    value={editPriority}
                    onChange={(e) => setEditPriority(e.target.value)}
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Category
                  </label>
                  <select
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none text-xs"
                    value={editCategory}
                    onChange={(e) => setEditCategory(e.target.value)}
                  >
                    <option value="Software">Software</option>
                    <option value="Hardware">Hardware</option>
                    <option value="Authentication">Authentication</option>
                    <option value="Billing">Billing</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Status
                  </label>
                  <select
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none text-xs"
                    value={editStatus}
                    onChange={(e) => setEditStatus(e.target.value)}
                  >
                    <option value="Open">Open</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Closed">Closed</option>
                  </select>
                </div>

                {updateStatus === 'error' && (
                  <div className="p-2.5 bg-red-950/20 border border-red-900/40 text-red-400 text-[10px] rounded-lg">
                    Failed to save changes. Try checking server logs.
                  </div>
                )}

                {updateStatus === 'success' && (
                  <div className="p-2.5 bg-green-950/20 border border-green-900/40 text-green-400 text-[10px] rounded-lg">
                    Changes saved successfully!
                  </div>
                )}
              </form>
            </div>

            <div className="border-t border-slate-800 pt-4 flex gap-3">
              <button 
                onClick={() => setEditingTicket(null)}
                className="flex-1 py-2.5 px-4 bg-slate-950 border border-slate-800 rounded-lg text-slate-400 hover:text-slate-300 text-xs font-bold"
              >
                Cancel
              </button>
              <button 
                onClick={handleUpdateTicket}
                disabled={updateStatus === 'updating'}
                className="flex-1 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold"
              >
                {updateStatus === 'updating' ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
