'use client';

import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

interface Alternative {
  alternative: string;
  vendor: string;
  final_cost: number;
  reason: string;
}

interface ComponentItem {
  component: string;
  selected_vendor: string;
  base_cost: number;
  final_cost: number;
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
            Smart BOM Alternatives Section
          </h3>
        </div>
        <span className="text-[10px] font-mono text-purple-400 bg-purple-950/40 px-2 py-0.5 border border-purple-900/30 rounded uppercase font-bold">
          Landed Cost Optimized
        </span>
      </div>

      {compWithAlts.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-500 font-mono">
          [SYSTEM NOTICE]: No alternative component suggestions compiled. Execute a design query.
        </div>
      ) : (
        <div className="space-y-6">
          {compWithAlts.map((comp, idx) => (
            <div key={idx} className="bg-zinc-950/40 border border-slate-800 rounded-lg p-5 space-y-3 font-mono text-xs">
              <div className="flex flex-col sm:flex-row justify-between sm:items-center pb-2 border-b border-slate-900 gap-1">
                <div>
                  <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px]">Original Component</span>
                  <h4 className="text-sm font-bold text-slate-200 mt-0.5">{comp.component}</h4>
                </div>
                <div className="text-left sm:text-right">
                  <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px]">Landed Cost</span>
                  <div className="text-slate-300 font-extrabold mt-0.5">
                    ₹{comp.final_cost.toLocaleString('en-IN')} <span className="text-[9px] font-normal text-slate-500">via {comp.selected_vendor}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-slate-500 font-bold uppercase tracking-widest text-[9px]">Alternative Options Ranked by Landed Cost</span>
                <div className="overflow-x-auto pt-1">
                  <table className="w-full text-left text-[11px] border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[9px]">
                        <th className="py-2 px-2">Alternative Component</th>
                        <th className="py-2 px-2">Optimal Vendor</th>
                        <th className="py-2 px-2 text-right">Landed Cost</th>
                        <th className="py-2 px-2">Optimization Reason</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-900/60">
                      {comp.alternatives?.map((alt, i) => (
                        <tr key={i} className="hover:bg-purple-950/5 transition-all">
                          <td className="py-2.5 px-2 text-purple-300 font-semibold flex items-center gap-1.5">
                            <ArrowRight className="w-3 h-3 text-purple-400 flex-shrink-0" />
                            {alt.alternative}
                          </td>
                          <td className="py-2.5 px-2 text-slate-300">{alt.vendor}</td>
                          <td className="py-2.5 px-2 text-right font-bold text-emerald-400">₹{alt.final_cost.toLocaleString('en-IN')}</td>
                          <td className="py-2.5 px-2 text-slate-400 max-w-xs truncate" title={alt.reason}>
                            {alt.reason}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
