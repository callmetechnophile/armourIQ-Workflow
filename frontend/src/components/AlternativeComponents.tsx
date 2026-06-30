'use client';

import React from 'react';
import { ArrowRight, Sparkles, AlertCircle, TrendingDown } from 'lucide-react';

interface Alternative {
  name: string;
  type: string;
  reason: string;
  approx_cost_usd: number;
}

interface ComponentItem {
  category: string;
  name: string;
  cost: number;
  notes: string;
  alternatives?: Alternative[];
}

interface AlternativeComponentsProps {
  components: ComponentItem[];
}

export default function AlternativeComponents({ components }: AlternativeComponentsProps) {
  const compWithAlts = components.filter(c => c.alternatives && c.alternatives.length > 0);

  return (
    <div className="glass-panel border border-purple-500/20 bg-slate-900/10 p-5 space-y-4">
      <div className="flex justify-between items-center border-b border-purple-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Alternative Component Finder
          </h3>
        </div>
        <span className="text-[10px] font-mono text-purple-400 bg-purple-950/40 px-2 py-0.5 border border-purple-900/30 rounded uppercase font-bold">
          Nemotron Powered
        </span>
      </div>

      {compWithAlts.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-500 font-mono">
          [SYSTEM NOTICE]: No alternative component suggestions found. Execute a design query.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {compWithAlts.map((comp, idx) => (
            <div key={idx} className="bg-zinc-950/40 border border-slate-800 rounded-lg p-4 space-y-3 font-mono text-xs">
              <div className="flex justify-between items-center pb-2 border-b border-slate-900">
                <span className="text-slate-400 font-bold max-w-[190px] truncate">{comp.name}</span>
                <span className="text-[10px] text-slate-500 font-bold">${comp.cost.toFixed(2)}</span>
              </div>

              <div className="space-y-3">
                {comp.alternatives?.map((alt, i) => {
                  let badgeColor = "bg-blue-950/40 border-blue-900/30 text-blue-400";
                  if (alt.type === "cheaper") {
                    badgeColor = "bg-emerald-950/40 border-emerald-900/30 text-emerald-400";
                  } else if (alt.type === "upgraded") {
                    badgeColor = "bg-purple-950/40 border-purple-900/30 text-purple-400";
                  }

                  return (
                    <div key={i} className="bg-slate-950/50 p-2.5 border border-slate-900 rounded space-y-1.5 hover:border-purple-500/20 transition-all">
                      <div className="flex justify-between items-center">
                        <span className="text-purple-300 font-semibold flex items-center gap-1">
                          <ArrowRight className="w-3 h-3 text-purple-400" />
                          {alt.name}
                        </span>
                        <span className={`text-[8px] font-extrabold uppercase px-1.5 py-0.5 border rounded ${badgeColor}`}>
                          {alt.type}
                        </span>
                      </div>
                      
                      <div className="text-[10px] text-slate-400 leading-normal flex items-start gap-1">
                        <TrendingDown className="w-3 h-3 text-slate-500 mt-0.5 flex-shrink-0" />
                        <span>{alt.reason}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
