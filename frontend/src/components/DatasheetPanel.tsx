'use client';

import React, { useState } from 'react';
import { FileText, ExternalLink, CheckCircle, ShieldAlert, ArrowRight } from 'lucide-react';

interface DatasheetItem {
  component: string;
  datasheet_link: string;
  source: string;
  trust_status: string;
}

interface DatasheetPanelProps {
  datasheets: DatasheetItem[];
}

export default function DatasheetPanel({ datasheets }: DatasheetPanelProps) {
  const [activePreview, setActivePreview] = useState<string | null>(null);

  if (!datasheets || datasheets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <FileText className="w-12 h-12 mb-2 stroke-1 text-slate-600 animate-pulse" />
        <p>No datasheets resolved for the current components.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Datasheets list */}
      <div className="lg:col-span-2 glass-panel p-6 border border-blue-500/20 bg-zinc-950/40">
        <h3 className="text-sm font-semibold text-cyan-400 glow-cyan mb-4 flex items-center gap-2 font-mono">
          <FileText className="w-4 h-4" />
          Component Technical Specifications
        </h3>

        <div className="space-y-3">
          {datasheets.map((item, idx) => (
            <div
              key={idx}
              className={`p-4 border rounded-lg transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 font-mono ${
                activePreview === item.datasheet_link
                  ? "bg-cyan-950/20 border-cyan-500/40"
                  : "bg-slate-900/20 border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="space-y-1.5">
                <h4 className="text-xs font-bold text-slate-200">{item.component}</h4>
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-[10px] text-slate-400">Publisher: {item.source}</span>
                  {item.trust_status === "TRUSTED" ? (
                    <span className="text-[9px] bg-emerald-950/60 border border-emerald-800 text-emerald-400 px-2 py-0.5 rounded flex items-center gap-1 font-bold">
                      <CheckCircle className="w-2.5 h-2.5" />
                      TRUSTED SOURCE
                    </span>
                  ) : item.trust_status === "VERIFIED" ? (
                    <span className="text-[9px] bg-blue-950/60 border border-blue-800 text-blue-400 px-2 py-0.5 rounded font-bold">
                      VERIFIED DISTRIBUTOR
                    </span>
                  ) : (
                    <span className="text-[9px] bg-amber-950/60 border border-amber-800 text-amber-400 px-2 py-0.5 rounded flex items-center gap-1 font-bold">
                      <ShieldAlert className="w-2.5 h-2.5" />
                      UNVERIFIED FALLBACK
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <button
                  onClick={() => setActivePreview(item.datasheet_link)}
                  className="text-[10px] bg-cyan-950/40 border border-cyan-800 hover:bg-cyan-900/40 px-3 py-1.5 rounded transition-all text-cyan-400 font-bold cursor-pointer"
                >
                  Inspect Link
                </button>
                <a
                  href={item.datasheet_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[10px] border border-slate-800 bg-slate-900 hover:bg-slate-800 px-3 py-1.5 rounded transition-all text-slate-300 flex items-center gap-1 cursor-pointer"
                >
                  Open PDF
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Preview Info Drawer */}
      <div className="lg:col-span-1">
        <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40 font-mono h-full flex flex-col justify-between">
          <div>
            <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-4">
              Datasheet Intelligence Preview
            </h4>
            {activePreview ? (
              <div className="space-y-4">
                <p className="text-xs text-slate-400 leading-relaxed">
                  You are inspecting the target document link. Click the button below to launch the manufacturer specification document.
                </p>
                <div className="p-3 bg-slate-950 border border-slate-900 rounded break-all text-[10px] text-slate-400 font-mono">
                  {activePreview}
                </div>
                <a
                  href={activePreview}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full text-center text-xs bg-cyan-950 border border-cyan-800 hover:bg-cyan-900 px-4 py-2 rounded text-cyan-400 flex items-center justify-center gap-1.5 font-bold transition-all cursor-pointer"
                >
                  Launch Datasheet Page
                  <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            ) : (
              <div className="text-xs text-slate-500 italic p-4 border border-slate-900 border-dashed rounded text-center">
                Select a component datasheet to preview url targets and publication sources.
              </div>
            )}
          </div>

          <div className="border-t border-slate-800 pt-4 mt-6 text-[10px] text-slate-500 space-y-1">
            <span className="font-bold text-slate-400 block">Security Scoping Policy:</span>
            <span>ArmorIQ mandates that all fetched links match verified manufacturer domains (e.g. espressif.com, nxp.com) to block phishing hazards.</span>
          </div>
        </div>
      </div>
      
      {/* Component Datasheet Links list */}
      <div className="lg:col-span-3 glass-panel p-6 border border-blue-500/20 bg-zinc-950/40 font-mono mt-6 space-y-4">
        <h3 className="text-sm font-semibold text-cyan-400 glow-cyan flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          Component Datasheet Links list
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Component name</th>
                <th className="py-2.5 px-3">datasheet link</th>
              </tr>
            </thead>
            <tbody>
              {datasheets.map((item, idx) => (
                <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/20 transition-all">
                  <td className="py-3 px-3 text-slate-200 font-semibold">{item.component}</td>
                  <td className="py-3 px-3">
                    <a 
                      href={item.datasheet_link} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="text-cyan-400 hover:text-cyan-300 break-all flex items-center gap-1.5"
                    >
                      {item.datasheet_link}
                      <ExternalLink className="w-3 h-3 shrink-0" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Copyable Markdown Format Area */}
        <div className="space-y-2 pt-2">
          <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase block">Copyable Markdown Format</span>
          <pre className="p-3 bg-slate-950 border border-slate-900 rounded text-[11px] text-slate-400 font-mono overflow-x-auto select-all max-h-[160px]">
{`Component name | datasheet link |\n` +
`---|---|\n` +
datasheets.map(item => `${item.component} | ${item.datasheet_link} |`).join('\n')}
          </pre>
        </div>
      </div>
    </div>
  );
}
