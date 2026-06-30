'use client';

import React from 'react';
import { Download, FileSpreadsheet, FileJson, FileText, CheckCircle2 } from 'lucide-react';

interface BOMExportPanelProps {
  apiBase: string;
  exports?: {
    csv: string;
    json: string;
    markdown: string;
  };
}

export default function BOMExportPanel({ apiBase, exports }: BOMExportPanelProps) {
  return (
    <div className="glass-panel border border-cyan-500/20 bg-slate-900/10 p-5 space-y-5">
      <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2.5">
          <FileSpreadsheet className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Bill of Materials Export
          </h3>
        </div>
        <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/40 px-2 py-0.5 border border-cyan-900/30 rounded uppercase font-bold">
          Package Exports
        </span>
      </div>

      <p className="text-[11px] font-mono text-slate-400 leading-relaxed">
        Download your finalized Bill of Materials, complete with component specs, optimized price alternates, and structural vendor sources.
      </p>

      {!exports ? (
        <div className="text-center py-6 text-xs text-slate-500 font-mono">
          [SYSTEM NOTICE]: BOM package is not compiled. Execute a design query.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* CSV Download */}
          <a
            href={`${apiBase}${exports.csv}`}
            download
            className="flex items-center justify-between p-4 bg-zinc-950/60 border border-slate-800 hover:border-emerald-500/30 rounded-lg hover:bg-emerald-950/10 transition-all font-mono text-xs text-slate-300"
          >
            <div className="flex items-center gap-2.5">
              <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
              <span>Export BOM CSV</span>
            </div>
            <Download className="w-4 h-4 text-slate-500" />
          </a>

          {/* JSON Download */}
          <a
            href={`${apiBase}${exports.json}`}
            download
            className="flex items-center justify-between p-4 bg-zinc-950/60 border border-slate-800 hover:border-cyan-500/30 rounded-lg hover:bg-cyan-950/10 transition-all font-mono text-xs text-slate-300"
          >
            <div className="flex items-center gap-2.5">
              <FileJson className="w-5 h-5 text-cyan-400" />
              <span>Export BOM JSON</span>
            </div>
            <Download className="w-4 h-4 text-slate-500" />
          </a>

          {/* Markdown Download */}
          <a
            href={`${apiBase}${exports.markdown}`}
            download
            className="flex items-center justify-between p-4 bg-zinc-950/60 border border-slate-800 hover:border-purple-500/30 rounded-lg hover:bg-purple-950/10 transition-all font-mono text-xs text-slate-300"
          >
            <div className="flex items-center gap-2.5">
              <FileText className="w-5 h-5 text-purple-400" />
              <span>Export BOM MD</span>
            </div>
            <Download className="w-4 h-4 text-slate-500" />
          </a>
        </div>
      )}
    </div>
  );
}
