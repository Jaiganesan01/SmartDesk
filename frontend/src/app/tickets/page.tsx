"use client";

import React, { useState } from 'react';
import { ClipboardList, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function CreateTicketForm() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('Medium');
  const [category, setCategory] = useState('Software');
  const [status, setStatus] = useState<'idle' | 'submitting' | 'error' | 'success'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setErrorMessage('Please fill in both the Title and Description fields.');
      setStatus('error');
      return;
    }

    setStatus('submitting');
    setErrorMessage('');

    try {
      const response = await fetch('/api/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, priority, category }),
      });

      if (!response.ok) {
        throw new Error(await response.text() || 'Failed to submit the ticket.');
      }

      setStatus('success');
      setTimeout(() => {
        router.push('/history');
      }, 1500);

    } catch (err: any) {
      setErrorMessage(err.message || 'An unexpected error occurred.');
      setStatus('error');
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-6 bg-slate-900/50 border border-slate-800 rounded-2xl p-8 shadow-xl text-slate-100 backdrop-blur-sm">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2 bg-indigo-950/60 border border-indigo-800 rounded-lg text-indigo-400">
          <ClipboardList className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
            Manual Ticket Dispatch
          </h1>
          <p className="text-slate-400 text-xs mt-0.5">
            Manually file support service tickets directly into the database.
          </p>
        </div>
      </div>

      <div className="h-px bg-slate-800 my-6"></div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Ticket Title
          </label>
          <input
            type="text"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors text-sm"
            placeholder="Summarize the core problem..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={status === 'submitting'}
          />
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Problem Description
          </label>
          <textarea
            rows={5}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors text-sm"
            placeholder="Describe the issue, reproduction steps, and impact in detail..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={status === 'submitting'}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Priority Level
            </label>
            <select
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors text-sm cursor-pointer"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={status === 'submitting'}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Issue Category
            </label>
            <select
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors text-sm cursor-pointer"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={status === 'submitting'}
            >
              <option value="Software">Software</option>
              <option value="Hardware">Hardware</option>
              <option value="Authentication">Authentication</option>
              <option value="Billing">Billing</option>
            </select>
          </div>
        </div>

        {/* Status Indicators */}
        {status === 'error' && (
          <div className="p-3 bg-red-950/30 border border-red-900/50 text-red-400 text-xs rounded-xl flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {status === 'success' && (
          <div className="p-3 bg-green-950/30 border border-green-900/50 text-green-400 text-xs rounded-xl flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Ticket dispatched successfully! Routing to history queue...</span>
          </div>
        )}

        <button
          type="submit"
          disabled={status === 'submitting'}
          className="w-full py-3 px-5 font-bold text-sm text-white rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:pointer-events-none transition-all shadow-lg shadow-indigo-950/40"
        >
          {status === 'submitting' ? 'Saving Ticket...' : 'Dispatch Ticket'}
        </button>
      </form>
    </div>
  );
}
