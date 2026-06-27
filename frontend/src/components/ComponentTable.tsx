'use client';

import React from 'react';
import { DollarSign, Layers } from 'lucide-react';

interface ComponentItem {
  category: string;
  name: string;
  cost: number;
  notes: string;
}

interface ComponentTableProps {
  components: ComponentItem[];
}

export default function ComponentTable({ components }: ComponentTableProps) {
  const totalCost = components.reduce((sum, item) => sum + item.cost, 0);

  if (!components || components.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <Layers className="w-12 h-12 mb-2 stroke-1 text-slate-600" />
        <p>No components extracted yet.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 border border-blue-500/20">
      <div className="flex justify-between items-center mb-4 border-b border-blue-900/40 pb-3">
        <h3 className="text-md font-semibold text-cyan-400 glow-cyan flex items-center gap-2">
          <Layers className="w-5 h-5" />
          Bill of Materials (BOM)
        </h3>
        <div className="text-xs text-slate-400 flex items-center gap-1.5 bg-slate-900/60 border border-slate-800 px-3 py-1.5 rounded-md font-mono">
          <span>Est. Budget:</span>
          <span className="text-emerald-400 font-bold font-mono text-sm">${totalCost.toFixed(2)}</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3">Component Name</th>
              <th className="py-2.5 px-3 text-right">Est. Cost</th>
              <th className="py-2.5 px-3">Integration Notes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {components.map((item, idx) => (
              <tr key={`comp-${idx}`} className="hover:bg-blue-500/5 transition-colors duration-150">
                <td className="py-3 px-3 font-semibold text-cyan-400/90 whitespace-nowrap">{item.category}</td>
                <td className="py-3 px-3 text-slate-200 font-medium">{item.name}</td>
                <td className="py-3 px-3 text-right font-bold text-emerald-400 font-mono">${item.cost.toFixed(2)}</td>
                <td className="py-3 px-3 text-slate-400 leading-relaxed max-w-xs">{item.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
