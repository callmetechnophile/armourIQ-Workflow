'use client';

import React, { useState } from 'react';
import { AlertOctagon, ShieldAlert, Play, Terminal, HelpCircle } from 'lucide-react';

interface ScopeViolationSimulatorProps {
  apiBase: string;
  onViolationTriggered?: () => void;
}

const TEST_CASES = [
  { agent: "Research Agent", tool: "export_pdf", label: "Research Agent ➔ export_pdf() [Illegal Export]" },
  { agent: "Validation Agent", tool: "optimize_components", label: "Validation Agent ➔ optimize_components() [Illegal Optimization]" },
  { agent: "Planner Agent", tool: "export_csv", label: "Planner Agent ➔ export_csv() [Illegal File Export]" }
];

export default function ScopeViolationSimulator({ apiBase, onViolationTriggered }: ScopeViolationSimulatorProps) {
  const [selectedCase, setSelectedCase] = useState(TEST_CASES[0]);
  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleSimulate = async () => {
    setSimulating(true);
    setResult(null);
    try {
      const res = await fetch(`${apiBase}/api/violations/simulate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          agent: selectedCase.agent,
          tool: selectedCase.tool
        })
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
        if (onViolationTriggered) {
          onViolationTriggered();
        }
      }
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="glass-panel border border-red-500/20 bg-slate-900/10 p-5 space-y-4">
      <div className="flex justify-between items-center border-b border-red-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <AlertOctagon className="w-5 h-5 text-red-500 animate-pulse" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Authority Violation Simulator
          </h3>
        </div>
        <span className="text-[9px] bg-red-950/40 border border-red-900/30 px-2 py-0.5 rounded font-mono text-red-400 font-bold uppercase tracking-wider">
          Testing Enforcer
        </span>
      </div>

      <p className="text-[11px] font-mono text-slate-400 leading-relaxed">
        Select a sandboxed agent and prompt it to run an out-of-scope system tool. ArmorIQ's active policy engine will intercept and block the action.
      </p>

      {/* Controller inputs */}
      <div className="flex flex-col sm:flex-row gap-3">
        <select 
          value={JSON.stringify(selectedCase)}
          onChange={(e) => setSelectedCase(JSON.parse(e.target.value))}
          className="flex-grow bg-slate-950 border border-slate-800 rounded p-2.5 text-xs font-mono text-slate-300 outline-none focus:border-red-500/40"
        >
          {TEST_CASES.map((tc, idx) => (
            <option key={idx} value={JSON.stringify(tc)}>
              {tc.label}
            </option>
          ))}
        </select>
        
        <button
          onClick={handleSimulate}
          disabled={simulating}
          className="bg-red-950/40 hover:bg-red-900/30 border border-red-950 hover:border-red-500 text-red-400 text-xs font-mono font-bold px-5 py-2.5 rounded transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-red-400" />
          {simulating ? "Violating..." : "Execute Simulation"}
        </button>
      </div>

      {/* Live Response Panel */}
      {result && (
        <div className="border border-red-500/30 bg-red-950/10 rounded-lg p-4 space-y-3 font-mono text-xs animate-fade-in">
          <div className="flex items-center gap-2 text-red-400 font-extrabold">
            <ShieldAlert className="w-4 h-4 text-red-500" />
            <span>[ARMORIQ ENFORCER ACTION: BLOCKED]</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px] pt-1">
            <div>
              <span className="text-slate-500">Violated Scope:</span>{" "}
              <span className="text-red-400 font-bold">{result.violated_scope}</span>
            </div>
            <div>
              <span className="text-slate-500">Requesting Agent:</span>{" "}
              <span className="text-slate-300">{result.requesting_agent}</span>
            </div>
            <div className="md:col-span-2">
              <span className="text-slate-500">Rejection Reason:</span>{" "}
              <span className="text-slate-200 leading-relaxed">{result.rejection_reason}</span>
            </div>
            <div className="md:col-span-2 bg-slate-950 p-2 border border-red-900/30 rounded text-[10px] flex items-center gap-2 overflow-x-auto">
              <Terminal className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
              <div>
                <div className="text-[8px] text-slate-500 uppercase tracking-widest font-bold">Blocked Receipt Hash</div>
                <div className="text-red-300 font-semibold">{result.blocked_receipt_hash}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
