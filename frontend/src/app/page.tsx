'use client';
// Vercel deployment rebuild trigger

import React, { useState, useEffect } from 'react';
import { Search, Mic, Sparkles, Download, ShieldCheck, RefreshCw, Layers, GitBranch, BookOpen, Calendar, Key, AlertTriangle, FileText, Check, Moon } from 'lucide-react';

// Components
import AgentPipeline from '@/components/AgentPipeline';
import AuditTrail from '@/components/AuditTrail';
import ScopeViolation from '@/components/ScopeViolation';
import ExecutionReadiness from '@/components/ExecutionReadiness';
import ComponentTable from '@/components/ComponentTable';
import DecisionTrace from '@/components/DecisionTrace';
import ResearchPapers from '@/components/ResearchPapers';
import GanttRoadmap from '@/components/GanttRoadmap';

const SUGGESTIONS = [
  "Voice controlled lights",
  "Solar tracker",
  "Smart greenhouse",
  "Bionic robotic hand"
];

export default function Home() {
  const [intent, setIntent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [pipelineData, setPipelineData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  
  // Audio wave fluctuation simulation
  const [waveHeights, setWaveHeights] = useState<number[]>([15, 30, 20, 40, 10, 30]);
  const [apiBase, setApiBase] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (process.env.NEXT_PUBLIC_API_URL) {
        setApiBase(process.env.NEXT_PUBLIC_API_URL);
      } else if (window.location.port === '3000') {
        setApiBase('http://localhost:8000');
      } else {
        setApiBase('');
      }
    }
  }, []);

  useEffect(() => {
    let interval: any;
    if (isRecording) {
      interval = setInterval(() => {
        setWaveHeights(Array.from({ length: 10 }, () => Math.floor(Math.random() * 35) + 5));
      }, 150);
    } else {
      setWaveHeights([15, 25, 10, 20, 8]);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleVoiceInput = () => {
    if (isRecording) {
      setIsRecording(false);
      setIntent("I want to build a solar powered vacuum cleaner");
    } else {
      setIsRecording(true);
      setIntent("Listening...");
    }
  };

  const handleSearchSubmit = async (searchIntent = intent) => {
    if (!searchIntent.trim() || searchIntent === "Listening...") return;
    
    setError(null);
    setPipelineData(null);
    setIsProcessing(true);
    setCurrentStepIndex(0);
    setActiveAgent("Planner Agent");

    try {
      // Fetch details from FastAPI backend
      const response = await fetch(`${apiBase}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent: searchIntent })
      });

      if (!response.ok) {
        throw new Error("Failed to generate engineering package. Ensure the FastAPI backend is running.");
      }

      const backendResult = await response.json();

      // Update recent searches
      if (!recentSearches.includes(searchIntent.toUpperCase())) {
        setRecentSearches([searchIntent.toUpperCase(), ...recentSearches.slice(0, 2)]);
      }

      // Step-by-step pipeline visualization
      const pipelineSteps = [
        "Planner Agent",
        "Retrieval Agent",
        "Extraction Agent",
        "Research Agent",
        "Validation Agent",
        "Optimization Agent",
        "Planning Agent",
        "Export Agent"
      ];

      for (let i = 0; i < pipelineSteps.length; i++) {
        setActiveAgent(pipelineSteps[i]);
        setCurrentStepIndex(i);
        await new Promise((resolve) => setTimeout(resolve, 850));
      }

      setPipelineData(backendResult);
      setActiveAgent(null);
      setCurrentStepIndex(-1);
      setIsProcessing(false);

    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
      setIsProcessing(false);
      setActiveAgent(null);
      setCurrentStepIndex(-1);
    }
  };

  const showResults = pipelineData && !isProcessing;

  return (
    <div 
      className="min-h-screen text-slate-100 flex flex-col relative overflow-x-hidden bg-slate-950/65 scanline"
      style={{
        backgroundImage: "linear-gradient(rgba(3, 7, 18, 0.72), rgba(3, 7, 18, 0.72)), url('/bg.png')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      {/* Top Navbar */}
      <header className="px-6 py-4 flex justify-between items-center z-10">
        {/* Top Left: Cyborg Icon */}
        <div className="flex items-center gap-1">
          <svg className="w-8 h-8 text-slate-200" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
            <circle cx="9" cy="9" r="1.5" />
            <circle cx="15" cy="9" r="1.5" />
            <path strokeLinecap="round" d="M12 12v2" />
          </svg>
        </div>

        {/* Top Right: Dark Mode Toggle */}
        <button className="p-2 rounded-full border border-zinc-800 bg-zinc-950/40 text-slate-300 hover:text-white hover:border-zinc-700 transition-all">
          <Moon className="w-4 h-4" />
        </button>
      </header>

      {/* Landing Layout Container */}
      {!showResults ? (
        <div className="flex-1 flex flex-col justify-center items-center px-4 max-w-4xl mx-auto w-full z-10 pb-20 mt-4 text-center">
          {/* Header Title Block */}
          <div className="bg-zinc-950/90 text-slate-100 font-mono tracking-[0.25em] px-5 py-2.5 text-2xl md:text-3xl font-extrabold uppercase border border-zinc-800 rounded-sm shadow-xl max-w-lg w-full">
            ARMOURFLOW AI
          </div>

          {/* Subtitle */}
          <h2 className="text-xs md:text-sm text-slate-200 tracking-[0.3em] font-extrabold mt-6 mb-2 uppercase">
            IDEA -&gt; RESEARCH -&gt; OPTIMIZE -&gt; EXECUTE
          </h2>

          {/* Description */}
          <p className="text-xs text-slate-400 italic mb-8">
            Hey Builder, What new ideas are running over your mind
          </p>

          {/* Search Pill Input */}
          <div className="bg-zinc-950/70 border border-zinc-850 rounded-full py-1.5 pl-6 pr-2.5 max-w-2xl w-full flex items-center justify-between shadow-2xl backdrop-blur-md mb-6 hover:border-zinc-700 transition-all duration-300">
            <input
              type="text"
              placeholder="I want to build a remote control car..."
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
              disabled={isProcessing}
              className="w-full bg-transparent border-0 outline-none text-slate-100 placeholder-slate-500 text-xs py-1.5 disabled:opacity-50"
            />
            
            <div className="flex items-center gap-3.5 flex-shrink-0">
              {isRecording && (
                <div className="flex items-end gap-0.5 h-6 px-1 bg-red-950/30 border border-red-500/20 rounded">
                  {waveHeights.map((h, i) => (
                    <div 
                      key={i} 
                      className="w-0.5 bg-red-500 rounded-t" 
                      style={{ height: `${h}%` }} 
                    />
                  ))}
                </div>
              )}
              
              <button
                onClick={handleVoiceInput}
                disabled={isProcessing}
                className={`p-2 rounded-full border transition-all ${
                  isRecording 
                    ? "bg-red-500 border-red-500 text-slate-950" 
                    : "bg-transparent border-transparent text-slate-400 hover:text-white"
                }`}
                title={isRecording ? "Stop Recording" : "Voice Input"}
              >
                <Mic className="w-4 h-4" />
              </button>

              <button
                onClick={() => handleSearchSubmit()}
                disabled={isProcessing || !intent.trim()}
                className="bg-zinc-900 hover:bg-zinc-850 text-slate-300 hover:text-white p-2.5 rounded-full border border-zinc-800 hover:border-zinc-700 transition-all disabled:opacity-40"
              >
                {isProcessing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Suggestions List */}
          <div className="space-y-3 mb-6">
            <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase block">SUGGESTIONS</span>
            <div className="flex flex-wrap justify-center gap-2 max-w-xl">
              {SUGGESTIONS.map((item, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setIntent(item);
                    handleSearchSubmit(item);
                  }}
                  disabled={isProcessing}
                  className="bg-zinc-950/70 border border-zinc-850 hover:border-zinc-700 text-slate-300 hover:text-white text-[11px] px-4 py-1.5 rounded-full transition-all disabled:opacity-50"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <div className="space-y-3 mb-6">
              <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase block">
                RECENT SEARCHES
              </span>
              <div className="flex justify-center">
                {recentSearches.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setIntent(item);
                      handleSearchSubmit(item);
                    }}
                    disabled={isProcessing}
                    className="bg-zinc-950/90 border border-zinc-850 hover:border-zinc-700 text-slate-300 hover:text-white text-[10px] font-bold px-4 py-1 rounded-full transition-all tracking-wide"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 bg-red-950/20 border border-red-500/30 rounded p-3 text-xs text-red-400 flex items-center gap-2 max-w-md">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Pipeline Active Loader */}
          {isProcessing && (
            <div className="mt-8 w-full max-w-4xl">
              <AgentPipeline 
                logs={pipelineData ? pipelineData.audit_trail : []} 
                activeAgent={activeAgent} 
                isProcessing={isProcessing} 
              />
            </div>
          )}

          {/* Bottom Branding Center */}
          <div className="absolute bottom-6 left-0 right-0 text-center space-y-1 select-none">
            <div className="text-[11px] font-black uppercase tracking-[0.2em] bg-gradient-to-r from-pink-500 to-indigo-400 bg-clip-text text-transparent">
              MULTI-MODEL WEB AGENT
            </div>
            <div className="text-[9px] text-slate-500 font-mono tracking-wider uppercase">
              ORGANISED COLLECTION OF IDEAS
            </div>
          </div>

          {/* Bottom Left Social links */}
          <div className="absolute bottom-6 left-6 flex items-center gap-2.5">
            <a 
              href="https://www.linkedin.com/in/mr.devgenius" 
              target="_blank" 
              rel="noreferrer"
              className="p-2 rounded-full border border-zinc-800 bg-zinc-950/40 text-slate-400 hover:text-white transition-all"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
              </svg>
            </a>
            <a 
              href="https://www.linkedin.com/in/callmetechnophile" 
              target="_blank" 
              rel="noreferrer"
              className="p-2 rounded-full border border-zinc-800 bg-zinc-950/40 text-slate-400 hover:text-white transition-all"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                <rect x="2" y="9" width="4" height="12"></rect>
                <circle cx="4" cy="4" r="2"></circle>
              </svg>
            </a>
          </div>

          {/* Bottom Right GitHub Link */}
          <div className="absolute bottom-6 right-6">
            <a 
              href="https://www.github.com/callmetechnophile" 
              target="_blank" 
              rel="noreferrer"
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-4 py-2.5 rounded-full shadow-lg shadow-indigo-600/25 transition-all flex items-center gap-1.5"
            >
              Star on GitHub ⭐
            </a>
          </div>
        </div>
      ) : (
        /* Results Dashboard view */
        <div className="max-w-7xl mx-auto px-4 mt-4 space-y-8 pb-16 z-10 w-full">
          {/* Header Title block in small format */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-zinc-950/80 border border-zinc-850 p-4 rounded-lg backdrop-blur-md">
            <div>
              <div className="text-xs font-mono tracking-widest text-cyan-400 font-extrabold uppercase">
                ArmourFlow AI (ArmorIQ)
              </div>
              <h2 className="text-sm font-bold text-slate-100 mt-1">
                Engineering Spec: <span className="text-slate-300 italic">"{pipelineData.intent}"</span>
              </h2>
            </div>

            {/* Micro input bar for search from results dashboard */}
            <div className="flex items-center gap-2 max-w-sm w-full">
              <input
                type="text"
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                placeholder="Submit new design target..."
                onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
                className="bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-xs w-full text-slate-100 placeholder-slate-500 outline-none"
              />
              <button
                onClick={() => handleSearchSubmit()}
                className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-3 py-1.5 rounded transition-all flex items-center gap-1.5"
              >
                <RefreshCw className="w-3 h-3" />
                Query
              </button>
            </div>
          </div>

          {/* Active Logs Pipeline overview */}
          <AgentPipeline 
            logs={pipelineData.audit_trail} 
            activeAgent={null} 
            isProcessing={false} 
          />

          {/* Execution Readiness circular dials */}
          <ExecutionReadiness 
            readiness={pipelineData.validation?.readiness_score || 80}
            risk={pipelineData.validation?.risk_score || 30}
            optimization={pipelineData.optimization?.optimization_score || 90}
          />

          {/* Scope Violation Enforcer block display */}
          <ScopeViolation logs={pipelineData.audit_trail} />

          {/* Components BOM */}
          <ComponentTable components={pipelineData.components} />

          {/* Research papers panels */}
          <ResearchPapers 
            papers={pipelineData.papers} 
            summary={pipelineData.paper_summary} 
          />

          {/* Decision Trace details */}
          <DecisionTrace decisions={pipelineData.decision_trace} />

          {/* Gantt Schedule roadmap */}
          <GanttRoadmap 
            roadmap={pipelineData.roadmap} 
            gantt={pipelineData.gantt} 
          />

          {/* Export spec buttons panel */}
          <div className="glass-panel p-6 border border-blue-500/20 bg-slate-900/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 mb-1 font-mono">
                <FileText className="w-4 h-4 text-cyan-400" />
                Download Spec Packages
              </h3>
              <p className="text-xs text-slate-400">
                Export complete engineering specifications, BOM quotes, and Gantt roadmap timeline.
              </p>
            </div>
            
            <div className="flex flex-wrap gap-3">
              <a
                href={`${apiBase}${pipelineData.exports?.pdf?.url}`}
                download
                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5 shadow-lg shadow-blue-500/10"
              >
                <Download className="w-3.5 h-3.5" />
                Export PDF
              </a>
              <a
                href={`${apiBase}${pipelineData.exports?.csv?.url}`}
                download
                className="bg-slate-900 hover:bg-slate-800 border border-slate-850 text-slate-300 text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                Export CSV
              </a>
              <a
                href={`${apiBase}${pipelineData.exports?.markdown?.url}`}
                download
                className="bg-slate-900 hover:bg-slate-800 border border-slate-850 text-slate-300 text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                Export Markdown
              </a>
            </div>
          </div>

          {/* Audit Verification Log panel */}
          <AuditTrail logs={pipelineData.audit_trail} />
        </div>
      )}
    </div>
  );
}
