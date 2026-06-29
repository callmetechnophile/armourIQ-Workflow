'use client';

import React, { useState } from 'react';
import { ListFilter, ShieldCheck, Key, Eye } from 'lucide-react';

interface AuditLog {
  agent: string;
  action: string;
  allowed_scope: string[];
  tool_invoked: string | null;
  status: string;
  details: string;
  receipt_id: string | null;
  parent_receipt_id: string | null;
}

interface AuditTrailProps {
  logs: AuditLog[];
}

export default function AuditTrail({ logs }: AuditTrailProps) {
  const [selectedReceipt, setSelectedReceipt] = useState<AuditLog | null>(null);

  if (!logs || logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <Key className="w-12 h-12 mb-2 stroke-1 text-slate-600" />
        <p>Audit trail will populate upon executing a research workflow.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 border border-blue-500/20">
        <div className="flex justify-between items-center mb-4 border-b border-blue-900/40 pb-3">
          <h3 className="text-md font-bold text-cyan-400 glow-cyan flex items-center gap-2">
            <Key className="w-5 h-5" />
            ArmorIQ Audit
          </h3>
          <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
            Logs Captured: {logs.length}
          </span>
        </div>

        <div className="overflow-x-auto max-h-[350px] overflow-y-auto pr-1">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px] sticky top-0 bg-slate-950 z-10 py-2">
                <th className="py-2.5 px-3">Agent</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Allowed Scope</th>
                <th className="py-2.5 px-3">Tool Invoked</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Receipt Hash</th>
                <th className="py-2.5 px-3 text-center">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {logs.map((log, idx) => {
                let statusColor = "text-slate-400";
                if (log.status === "SUCCESS") statusColor = "text-emerald-400 font-medium";
                else if (log.status === "BLOCKED") statusColor = "text-red-400 font-extrabold";
                else if (log.status === "FAILED") statusColor = "text-amber-500";

                return (
                  <tr key={`audit-${idx}`} className="hover:bg-blue-500/5 transition-colors duration-150">
                    <td className="py-2.5 px-3 font-semibold text-slate-300">{log.agent}</td>
                    <td className="py-2.5 px-3 font-mono text-[10px] text-cyan-400">{log.action}</td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[9px] max-w-[120px] truncate">
                      {log.allowed_scope.length > 0 ? log.allowed_scope.join(", ") : "N/A"}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[10px] text-slate-300">
                      {log.tool_invoked || "—"}
                    </td>
                    <td className={`py-2.5 px-3 text-[10px] ${statusColor}`}>{log.status}</td>
                    <td className="py-2.5 px-3 font-mono text-[9px] text-slate-500">
                      {log.receipt_id ? `${log.receipt_id.substring(0, 13)}...` : "N/A"}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <button
                        onClick={() => setSelectedReceipt(log)}
                        className="text-cyan-400 hover:text-cyan-300 transition-colors inline-flex p-1"
                        title="View Token Metadata"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Receipt Detail Modal overlay */}
      {selectedReceipt && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="glass-panel p-6 border border-cyan-500/30 max-w-lg w-full bg-slate-950 relative">
            <h4 className="text-sm font-bold text-cyan-400 flex items-center gap-1.5 border-b border-slate-800 pb-3 mb-4 font-mono">
              <ShieldCheck className="w-5 h-5 text-cyan-500" />
              Cryptographic Receipt Verification
            </h4>
            
            <div className="space-y-3.5 text-xs font-mono">
              <div className="grid grid-cols-3 border-b border-slate-900/50 pb-2">
                <span className="text-slate-500">Agent Name:</span>
                <span className="text-slate-200 col-span-2">{selectedReceipt.agent}</span>
              </div>
              <div className="grid grid-cols-3 border-b border-slate-900/50 pb-2">
                <span className="text-slate-500">Operation:</span>
                <span className="text-cyan-400 col-span-2">{selectedReceipt.action}</span>
              </div>
              <div className="grid grid-cols-3 border-b border-slate-900/50 pb-2">
                <span className="text-slate-500">Allowed Scope:</span>
                <span className="text-slate-300 col-span-2 font-bold">
                  {selectedReceipt.allowed_scope.length > 0 
                    ? `[${selectedReceipt.allowed_scope.join(", ")}]` 
                    : "[]"}
                </span>
              </div>
              <div className="grid grid-cols-3 border-b border-slate-900/50 pb-2">
                <span className="text-slate-500">Tool Executed:</span>
                <span className="text-slate-300 col-span-2">{selectedReceipt.tool_invoked || "None"}</span>
              </div>
              <div className="grid grid-cols-3 border-b border-slate-900/50 pb-2">
                <span className="text-slate-500">Receipt ID:</span>
                <span className="text-slate-400 col-span-2 text-[10px] select-all">{selectedReceipt.receipt_id || "N/A"}</span>
              </div>
              <div className="grid grid-cols-3 border-b border-slate-900/50 pb-2">
                <span className="text-slate-500">Parent ID:</span>
                <span className="text-slate-500 col-span-2 text-[10px]">{selectedReceipt.parent_receipt_id || "Root Plan"}</span>
              </div>
              <div className="grid grid-cols-3">
                <span className="text-slate-500">Log Details:</span>
                <span className="text-slate-300 col-span-2 leading-relaxed">{selectedReceipt.details}</span>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setSelectedReceipt(null)}
                className="bg-cyan-950 border border-cyan-500/40 text-cyan-400 px-4 py-1.5 rounded text-xs font-semibold hover:bg-cyan-500/20 hover:text-white transition-all"
              >
                Close Receipt Verification
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
