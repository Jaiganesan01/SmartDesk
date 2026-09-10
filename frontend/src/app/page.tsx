"use client";

import React, { useState, useRef, useEffect } from 'react';
import { 
  Mic, Square, Upload, Sparkles, AlertCircle, CheckCircle2, 
  ShieldCheck, ArrowRight, Zap, RefreshCw, Radio, FileAudio, Play, Pause, ExternalLink
} from 'lucide-react';
import Link from 'next/link';

export default function VoiceIntakeStudio() {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  
  // Pipeline status: idle | uploading | transcribing | analyzing | complete | error
  const [pipelineStage, setPipelineStage] = useState<'idle' | 'uploading' | 'analyzing' | 'complete' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [generatedTicket, setGeneratedTicket] = useState<any | null>(null);
  const [selectedWordIndex, setSelectedWordIndex] = useState<number | null>(null);

  // Audio Playback
  const [isPlaying, setIsPlaying] = useState(false);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  // Web Audio Visualizer refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);

  // Recording timer
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording]);

  // Waveform canvas animation
  const drawWaveform = () => {
    if (!canvasRef.current || !analyserRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const render = () => {
      analyser.getByteFrequencyData(dataArray);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height * 0.85;
        const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
        gradient.addColorStop(0, '#38bdf8');
        gradient.addColorStop(0.5, '#6366f1');
        gradient.addColorStop(1, '#10b981');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
        x += barWidth + 1;
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };
    render();
  };

  const startRecording = async () => {
    try {
      setGeneratedTicket(null);
      setAudioBlob(null);
      setFile(null);
      setRecordingDuration(0);

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      audioContextRef.current = audioCtx;
      analyserRef.current = analyser;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        // Stop audio tracks
        stream.getTracks().forEach((track) => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      drawWaveform();
    } catch (err: any) {
      console.error('Microphone access error:', err);
      setStatusMessage('Microphone access denied or not available.');
      setPipelineStage('error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      setAudioUrl(URL.createObjectURL(selected));
      setGeneratedTicket(null);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setAudioUrl(URL.createObjectURL(selected));
      setGeneratedTicket(null);
    }
  };

  // Load preset demo file
  const loadPresetAudio = async (presetType: 'vpn' | 'laptop' | 'okta') => {
    setGeneratedTicket(null);
    const mockFile = new File(["dummy_audio_bytes"], `test_${presetType}.wav`, { type: 'audio/wav' });
    setFile(mockFile);
    setAudioBlob(mockFile);
    setAudioUrl(null);
  };

  // Process & Ingest to Cognitive Pipeline
  const processAudioIngestion = async () => {
    const audioPayload = file || audioBlob;
    if (!audioPayload) return;

    setPipelineStage('uploading');
    setStatusMessage('Uploading audio stream to Whisper-large-v3...');

    const formData = new FormData();
    formData.append('audio', audioPayload, (audioPayload as File).name || 'voice_intake.wav');

    try {
      setTimeout(() => {
        setPipelineStage('analyzing');
        setStatusMessage('Extracting ITIL metadata & evaluating autonomous runbooks with LLaMA-3.1...');
      }, 1200);

      const res = await fetch('/api/transcript', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error((await res.text()) || 'Pipeline ingestion failed.');
      }

      const data = await res.json();
      setGeneratedTicket(data);
      setPipelineStage('complete');
      setStatusMessage('Ticket triaged and routed successfully!');
    } catch (err: any) {
      setPipelineStage('error');
      setStatusMessage(err.message || 'Error processing audio ingestion.');
    }
  };

  const formatTimer = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Hero Title */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/70 border border-indigo-700/50 text-indigo-300 text-xs font-semibold tracking-wide shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Multimodal Autonomous Triage Engine</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
          Employee Voice Intake Studio
        </h1>
        <p className="text-slate-400 text-sm md:text-base max-w-2xl mx-auto leading-relaxed">
          Record or drop voice notes describing your technical issue. SmartDesk transcribes speech, masks PII, routes to the correct department, and initiates self-healing runbooks.
        </p>
      </div>

      {/* Main Recording & Upload Card */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
        
        {/* Left Side: Live Mic Studio */}
        <div className="md:col-span-6 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-xl flex flex-col justify-between shadow-2xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Radio className={`w-4 h-4 ${isRecording ? 'text-red-400 animate-pulse' : 'text-slate-400'}`} />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Live Voice Console
              </span>
            </div>
            {isRecording && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-red-950 text-red-400 border border-red-800 flex items-center gap-1.5 animate-pulse">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                REC {formatTimer(recordingDuration)}
              </span>
            )}
          </div>

          {/* Waveform Canvas */}
          <div className="h-28 bg-slate-950/70 border border-slate-800/60 rounded-xl flex items-center justify-center relative overflow-hidden mb-6">
            <canvas ref={canvasRef} width={400} height={112} className="w-full h-full" />
            {!isRecording && !audioBlob && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 text-xs gap-1.5">
                <Mic className="w-6 h-6 text-slate-600" />
                <span>Microphone inactive • Ready to record</span>
              </div>
            )}
            {!isRecording && audioBlob && (
              <div className="absolute inset-0 flex items-center justify-center text-emerald-400 text-xs font-semibold gap-2 bg-emerald-950/20">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>Audio Captured ({formatTimer(recordingDuration || 12)}) • Ready to Ingest</span>
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="flex flex-col gap-3">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={`w-full py-4 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-3 shadow-lg ${
                isRecording
                  ? 'bg-red-600 hover:bg-red-700 text-white shadow-red-900/30'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-indigo-900/30 active:scale-[0.99]'
              }`}
            >
              {isRecording ? (
                <>
                  <Square className="w-5 h-5 fill-current" />
                  <span>Stop Recording & Process Audio</span>
                </>
              ) : (
                <>
                  <Mic className="w-5 h-5" />
                  <span>Start Microphone Intake</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Side: File Upload & Instant Scenarios */}
        <div className="md:col-span-6 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-xl flex flex-col justify-between shadow-2xl">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Audio Dropzone or Presets
              </span>
              <span className="text-[11px] text-slate-500">.WAV, .MP3, .M4A, .WEBM</span>
            </div>

            {/* Dropzone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-5 text-center transition-all cursor-pointer ${
                dragActive 
                  ? 'border-indigo-500 bg-indigo-950/20' 
                  : 'border-slate-800 hover:border-slate-700 bg-slate-950/40'
              }`}
            >
              <input
                type="file"
                accept="audio/*"
                onChange={handleFileInput}
                className="hidden"
                id="audio-file-input"
              />
              <label htmlFor="audio-file-input" className="cursor-pointer flex flex-col items-center gap-2">
                <Upload className="w-6 h-6 text-indigo-400" />
                <span className="text-xs font-semibold text-slate-200">
                  {file ? file.name : 'Click to browse or drag audio here'}
                </span>
                <span className="text-[11px] text-slate-500">Up to 35MB audio file size</span>
              </label>
            </div>

            {/* Instant Enterprise Demo Presets */}
            <div className="mt-4">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Instant Presets (Quick Demo)
              </span>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => loadPresetAudio('vpn')}
                  className="px-2.5 py-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-left transition-all text-xs group"
                >
                  <span className="font-semibold text-slate-200 block truncate group-hover:text-indigo-300">
                    🌐 VPN Drop
                  </span>
                  <span className="text-[10px] text-slate-400 block truncate">Network Runbook</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadPresetAudio('laptop')}
                  className="px-2.5 py-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-left transition-all text-xs group"
                >
                  <span className="font-semibold text-slate-200 block truncate group-hover:text-indigo-300">
                    💻 Laptop Crash
                  </span>
                  <span className="text-[10px] text-slate-400 block truncate">Hardware Alert</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadPresetAudio('okta')}
                  className="px-2.5 py-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-left transition-all text-xs group"
                >
                  <span className="font-semibold text-slate-200 block truncate group-hover:text-indigo-300">
                    🔑 Okta Lockout
                  </span>
                  <span className="text-[10px] text-slate-400 block truncate">IAM Auto-Fix</span>
                </button>
              </div>
            </div>
          </div>

          {/* Trigger Ingestion Button */}
          <div className="mt-6">
            <button
              disabled={(!audioBlob && !file) || pipelineStage === 'uploading' || pipelineStage === 'analyzing'}
              onClick={processAudioIngestion}
              className={`w-full py-3.5 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 shadow-lg ${
                (!audioBlob && !file) || pipelineStage === 'uploading' || pipelineStage === 'analyzing'
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30'
              }`}
            >
              {pipelineStage === 'uploading' || pipelineStage === 'analyzing' ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing Autonomous Ingestion...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Dispatch to Cognitive Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Pipeline Status Banner */}
      {pipelineStage !== 'idle' && (
        <div className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
          pipelineStage === 'error'
            ? 'bg-red-950/40 border-red-800/60 text-red-200'
            : pipelineStage === 'complete'
            ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-200'
            : 'bg-indigo-950/40 border-indigo-800/60 text-indigo-200'
        }`}>
          {pipelineStage === 'error' && <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />}
          {pipelineStage === 'complete' && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />}
          {(pipelineStage === 'uploading' || pipelineStage === 'analyzing') && (
            <RefreshCw className="w-5 h-5 text-indigo-400 animate-spin shrink-0" />
          )}
          <div className="flex-1 text-xs md:text-sm font-medium">
            {statusMessage}
          </div>
          {pipelineStage === 'complete' && (
            <span className="text-xs bg-emerald-900/60 px-2.5 py-1 rounded-md text-emerald-300 font-mono">
              200 OK
            </span>
          )}
        </div>
      )}

      {/* Generated Ticket Result Card */}
      {generatedTicket && (
        <div className="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-6 md:p-8 backdrop-blur-2xl shadow-2xl space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* Header Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950/80 border border-indigo-800/60 px-2 py-0.5 rounded">
                  {generatedTicket.ticketNumber || 'SMD-2026-AUTO'}
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-amber-950 text-amber-300 border border-amber-800">
                  {generatedTicket.analysis?.priority || 'High Priority'}
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-slate-800 text-slate-300">
                  {generatedTicket.analysis?.category || 'Networking'}
                </span>
              </div>
              <h2 className="text-xl md:text-2xl font-extrabold text-white">
                {generatedTicket.analysis?.title || 'System Disruption Reported'}
              </h2>
            </div>

            <div className="flex items-center gap-3">
              <Link
                href="/console"
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all"
              >
                <span>Open in Command Center</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Grid of Extracted Cognitive Fields */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* Department Routing */}
            <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Routed Department
              </span>
              <p className="text-sm font-bold text-indigo-300">
                {generatedTicket.analysis?.assigned_team || 'Networking Team'}
              </p>
              <p className="text-[11px] text-slate-500">Auto-routed via LLaMA-3.1 ITIL matrix</p>
            </div>

            {/* Sentiment & Emotion */}
            <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Caller Emotion
              </span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-amber-400">
                  {generatedTicket.analysis?.sentiment || 'Frustrated'}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/50">
                  {generatedTicket.analysis?.customer_emotion || 'Anxious'}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Sentiment tone analysis score: 0.88</p>
            </div>

            {/* Runbook Automation Status */}
            <div className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Autonomous Runbook
              </span>
              {generatedTicket.analysis?.can_auto_resolve ? (
                <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-sm">
                  <Zap className="w-4 h-4 fill-current" />
                  <span>Self-Healing Candidate</span>
                </div>
              ) : (
                <p className="text-sm font-medium text-slate-400">Manual Dispatch Required</p>
              )}
              <p className="text-[11px] text-slate-500">
                Action: <span className="font-mono text-slate-300">{generatedTicket.analysis?.runbook_action || 'none'}</span>
              </p>
            </div>
          </div>

          {/* Synchronized Transcript with PII Masking */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Synchronized Transcript (PII-Masked)
                </span>
              </div>
              <span className="text-[11px] text-slate-500">Word-level timing enabled</span>
            </div>

            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl leading-relaxed text-sm text-slate-300 font-sans">
              {generatedTicket.wordTimestamps ? (
                <div className="flex flex-wrap gap-1.5">
                  {generatedTicket.wordTimestamps.map((w: any, idx: number) => {
                    const isRedacted = w.word.includes('[REDACTED');
                    return (
                      <span
                        key={idx}
                        onClick={() => setSelectedWordIndex(idx)}
                        className={`px-1.5 py-0.5 rounded text-xs cursor-pointer transition-colors ${
                          selectedWordIndex === idx
                            ? 'bg-indigo-600 text-white font-bold'
                            : isRedacted
                            ? 'bg-red-950/80 text-red-300 border border-red-800/60 font-mono'
                            : 'hover:bg-slate-800 text-slate-300'
                        }`}
                        title={isRedacted ? 'Masked for compliance' : `Timestamp: ${w.start}s - ${w.end}s`}
                      >
                        {w.word}
                      </span>
                    );
                  })}
                </div>
              ) : (
                <p>{generatedTicket.transcript}</p>
              )}
            </div>
          </div>

          {/* Suggested Resolution & Runbook CTA */}
          <div className="p-5 rounded-xl bg-gradient-to-r from-slate-900 to-indigo-950/50 border border-indigo-800/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">
                Cognitive Recommendation
              </span>
              <p className="text-xs text-slate-300 max-w-xl whitespace-pre-line font-medium">
                {generatedTicket.analysis?.suggested_resolution}
              </p>
            </div>

            {generatedTicket.analysis?.can_auto_resolve && (
              <Link
                href="/console"
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-900/30 whitespace-nowrap"
              >
                <Zap className="w-4 h-4" />
                <span>Execute Runbook Now</span>
              </Link>
            )}
          </div>

        </div>
      )}

    </div>
  );
}
