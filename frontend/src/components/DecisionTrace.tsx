'use client';

import React from 'react';
import { GitBranch, ShieldCheck } from 'lucide-react';

interface DecisionItem {
  decision: string;
  rationale: string;
  agent: string;
}

interface DecisionTraceProps {
  decisions: DecisionItem[];
}

export default function DecisionTrace({ decisions }: DecisionTraceProps) {
  if (!decisions || decisions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <GitBranch className="w-12 h-12 mb-2 stroke-1 text-slate-600" />
        <p>No decision trace recorded.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 border border-blue-500/20">
      <div className="flex justify-between items-center mb-4 border-b border-blue-900/40 pb-3">
        <h3 className="text-md font-semibold text-cyan-400 glow-cyan flex items-center gap-2">
          <GitBranch className="w-5 h-5" />
          Engineering Decision Trace
        </h3>
        <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-500" />
          Verifiable Chain of Logic
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
              <th className="py-2.5 px-3">Decision Taken</th>
              <th className="py-2.5 px-3">Technical Rationale</th>
              <th className="py-2.5 px-3">Responsible Agent</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {decisions.map((item, idx) => (
              <tr key={`decision-${idx}`} className="hover:bg-blue-500/5 transition-colors duration-150">
                <td className="py-3 px-3 text-slate-200 font-semibold max-w-xs">{item.decision}</td>
                <td className="py-3 px-3 text-slate-400 leading-relaxed max-w-sm">{item.rationale}</td>
                <td className="py-3 px-3 font-mono text-[10px] text-cyan-400 whitespace-nowrap bg-blue-950/20 px-2 py-1 rounded border border-blue-900/30 w-fit inline-block my-2">
                  {item.agent}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
