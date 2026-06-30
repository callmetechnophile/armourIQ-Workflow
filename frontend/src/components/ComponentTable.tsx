'use client';

import React from 'react';
import { Layers } from 'lucide-react';

interface ComponentItem {
  component: string;
  category: string;
  selected_vendor: string;
  vendor_location: string;
  base_cost: number;
  shipping_cost: number;
  distance: string;
  final_cost: number;
  stock: string;
  eta: string;
  url?: string;
}

interface ComponentTableProps {
  components: ComponentItem[];
}

export default function ComponentTable({ components }: ComponentTableProps) {
  const totalLandedCost = components.reduce((sum, item) => sum + (item.final_cost || 0), 0);

  if (!components || components.length === 0 || !components[0].selected_vendor) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <Layers className="w-12 h-12 mb-2 stroke-1 text-slate-600" />
        <p>No optimized components compiled yet.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40">
      <div className="flex justify-between items-center mb-4 border-b border-blue-900/40 pb-3">
        <h3 className="text-md font-semibold text-cyan-400 glow-cyan flex items-center gap-2">
          <Layers className="w-5 h-5" />
          Smart BOM Optimization Engine
        </h3>
        <div className="text-xs text-slate-400 flex items-center gap-1.5 bg-slate-900/60 border border-slate-800 px-3 py-1.5 rounded-md font-mono">
          <span>Final Landed Budget:</span>
          <span className="text-emerald-400 font-bold font-mono text-sm">₹{totalLandedCost.toLocaleString('en-IN')}</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
              <th className="py-2.5 px-3">Component</th>
              <th className="py-2.5 px-3">Optimal Vendor</th>
              <th className="py-2.5 px-3 text-right">Base Cost</th>
              <th className="py-2.5 px-3 text-right">Shipping</th>
              <th className="py-2.5 px-3 text-right">Distance</th>
              <th className="py-2.5 px-3 text-right">Final Cost</th>
              <th className="py-2.5 px-3 text-center">Stock</th>
              <th className="py-2.5 px-3 text-right">ETA</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {components.map((item, idx) => (
              <tr key={`comp-${idx}`} className="hover:bg-blue-500/5 transition-colors duration-150">
                <td className="py-3 px-3 text-slate-200 font-medium">{item.component}</td>
                <td className="py-3 px-3 text-cyan-400 font-semibold whitespace-nowrap">
                  {item.url ? (
                    <a 
                      href={item.url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="hover:underline"
                    >
                      {item.selected_vendor}
                    </a>
                  ) : (
                    item.selected_vendor
                  )}
                </td>
                <td className="py-3 px-3 text-right font-bold text-slate-300">₹{item.base_cost.toLocaleString('en-IN')}</td>
                <td className="py-3 px-3 text-right text-slate-400">
                  {item.shipping_cost === 0 ? "Free" : `₹${item.shipping_cost.toLocaleString('en-IN')}`}
                </td>
                <td className="py-3 px-3 text-right text-slate-400">{item.distance}</td>
                <td className="py-3 px-3 text-right font-bold text-emerald-400">₹{item.final_cost.toLocaleString('en-IN')}</td>
                <td className="py-3 px-3 text-center">
                  <span className={`inline-block text-[9px] px-1.5 py-0.5 rounded border ${
                    item.stock === "In Stock" 
                      ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-400"
                      : "bg-amber-950/20 border-amber-500/30 text-amber-400"
                  }`}>
                    {item.stock}
                  </span>
                </td>
                <td className="py-3 px-3 text-right text-cyan-300 font-semibold whitespace-nowrap">{item.eta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
