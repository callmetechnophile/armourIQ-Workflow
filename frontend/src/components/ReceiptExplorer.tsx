'use client';

import React, { useEffect, useState } from 'react';
import { FileSearch, Clock, ShieldCheck, ShieldAlert, Key, ChevronDown, ChevronRight } from 'lucide-react';

interface Receipt {
  agent: string;
  parent: string;
  tool: string;
  scope: string[];
  timestamp: string;
  hash: string;
  status: string;
  execution_result?: string;
  authority_chain?: string;
}

interface ReceiptExplorerProps {
  apiBase: string;
  refreshTrigger?: number;
}

export default function ReceiptExplorer({ apiBase, refreshTrigger }: ReceiptExplorerProps) {
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedHash, setExpandedHash] = useState<string | null>(null);

  const fetchReceipts = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/receipts`);
      if (res.ok) {
        const data = await res.json();
        setReceipts(data);
      }
    } catch (err) {
      console.error("Failed to load cryptographic receipts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReceipts();
  }, [apiBase, refreshTrigger]);

  const toggleExpand = (hash: string) => {
    setExpandedHash(expandedHash === hash ? null : hash);
  };

  const formatTime = (tsStr: string) => {
    try {
      const ts = parseFloat(tsStr);
      return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return tsStr;
    }
  };

  return (
    <div className="glass-panel border border-blue-500/20 bg-slate-900/10 p-5">
      <div className="flex justify-between items-center mb-5 border-b border-blue-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <FileSearch className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Cryptographic Receipt Explorer
          </h3>
        </div>
        <button 
          onClick={fetchReceipts}
          className="text-[10px] font-mono bg-blue-950/40 px-2.5 py-1 border border-blue-900/30 rounded text-cyan-400 hover:bg-blue-900/40 transition-all cursor-pointer"
        >
          {loading ? "Syncing..." : "Sync Receipts"}
        </button>
      </div>

      {receipts.length === 0 ? (
        <div className="text-center py-8 text-xs text-slate-500 font-mono">
          [SYSTEM NOTICE]: No receipts archived. Execute a design query to generate cryptographic logs.
        </div>
      ) : (
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
          {receipts.map((rcpt) => {
            const isExpanded = expandedHash === rcpt.hash;
            const isSuccess = rcpt.status === "success";
            
            return (
              <div 
                key={rcpt.hash} 
                className={`border rounded-lg transition-all ${
                  isExpanded 
                    ? "border-blue-500/40 bg-zinc-950/80" 
                    : "border-slate-800/80 bg-zinc-950/40 hover:bg-zinc-950/60"
                }`}
              >
                {/* Header Row */}
                <div 
                  className="flex items-center justify-between p-3 cursor-pointer select-none text-xs font-mono"
                  onClick={() => toggleExpand(rcpt.hash)}
                >
                  <div className="flex items-center gap-3">
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-blue-400" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{formatTime(rcpt.timestamp)}</span>
                    </div>
                    <span className="font-bold text-slate-200">{rcpt.agent}</span>
                    <span className="text-[10px] text-cyan-400 bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded font-mono">
                      {rcpt.tool}
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-[9px] text-slate-500 font-mono max-w-[80px] truncate">
                      {rcpt.hash.slice(0, 12)}...
                    </span>
                    <span className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded text-[9px] font-extrabold border ${
                      isSuccess 
                        ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-400"
                        : "bg-red-950/20 border-red-500/30 text-red-400"
                    }`}>
                      {isSuccess ? <ShieldCheck className="w-3 h-3" /> : <ShieldAlert className="w-3 h-3" />}
                      {rcpt.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* Expanded JSON details */}
                {isExpanded && (
                  <div className="p-4 border-t border-slate-900/80 space-y-3 font-mono text-[10px]">
                    {/* Authority chain */}
                    <div className="bg-slate-900/40 p-2.5 rounded border border-slate-800/60 flex items-center gap-2">
                      <Key className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                      <div>
                        <div className="text-[8px] uppercase text-slate-500 tracking-wider font-bold">Authority Chain</div>
                        <div className="text-slate-300 text-[10px] font-semibold">{rcpt.authority_chain || "Planner Agent"}</div>
                      </div>
                    </div>

                    {/* Metadata JSON display */}
                    <div>
                      <div className="text-[8px] uppercase text-slate-500 tracking-wider font-bold mb-1">Receipt Hash Data</div>
                      <pre className="w-full bg-slate-950 p-3 rounded border border-slate-800/80 text-blue-300 overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-[220px]">
                        {JSON.stringify({
                          agent: rcpt.agent,
                          parent: rcpt.parent,
                          tool: rcpt.tool,
                          scope: rcpt.scope,
                          timestamp: rcpt.timestamp,
                          hash: rcpt.hash,
                          status: rcpt.status,
                          execution_result: rcpt.execution_result || "N/A"
                        }, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
