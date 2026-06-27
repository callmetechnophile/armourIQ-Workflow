'use client';

import React from 'react';
import { ShieldAlert, AlertCircle } from 'lucide-react';

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

interface ScopeViolationProps {
  logs: AuditLog[];
}

export default function ScopeViolation({ logs }: ScopeViolationProps) {
  // Filter all BLOCKED audit log items
  const blockedLogs = logs.filter((log) => log.status === "BLOCKED");

  return (
    <div className="glass-panel p-6 border border-zinc-800 bg-[#090d16]/80 relative overflow-hidden rounded-lg shadow-xl">
      {/* Title Header bar */}
      <div className="flex justify-between items-center mb-6 border-b border-zinc-800/60 pb-3">
        <h3 className="text-sm font-bold text-red-400 glow-red flex items-center gap-2.5">
          <ShieldAlert className="w-5 h-5 text-red-500" />
          ArmorIQ Scope Violation & Block Log
        </h3>
        <span className="text-[9px] font-mono font-extrabold tracking-widest text-red-500 border border-red-500/20 bg-red-950/20 px-2.5 py-1 rounded">
          ENFORCER ACTIVE
        </span>
      </div>

      {blockedLogs.length > 0 ? (
        <div className="space-y-4">
          {blockedLogs.map((log, idx) => (
            <div 
              key={`violation-${idx}`} 
              className="border border-red-950/40 bg-red-950/5 rounded-lg p-5 space-y-4"
            >
              {/* Header: Unauthorized attempt block */}
              <div className="flex items-start gap-3">
                <div className="w-5 h-5 rounded-full border border-red-500/35 flex items-center justify-center flex-shrink-0 mt-0.5 bg-red-950/20">
                  <span className="text-xs font-bold text-red-500">!</span>
                </div>
                <div className="space-y-1">
                  <h4 className="text-xs font-extrabold text-red-500 uppercase tracking-wide font-mono">
                    UNAUTHORIZED TOOL EXECUTION ATTEMPT BLOCKED!
                  </h4>
                  <p className="text-xs text-slate-300">
                    Agent <span className="font-bold text-slate-100">"{log.agent}"</span> attempted to call tool{" "}
                    <span className="font-bold text-red-400">"{log.tool_invoked}"</span>.
                  </p>
                </div>
              </div>

              {/* Columns: Scope and Receipt Hash */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
                <div className="space-y-1">
                  <span className="text-slate-500 block text-[11px] font-medium">Agent Authorized Scope:</span>
                  <span className="text-cyan-400 font-bold font-mono">
                    {log.allowed_scope.length > 0 ? `[${log.allowed_scope.join(", ")}]` : "[]"}
                  </span>
                </div>
                
                <div className="space-y-1">
                  <span className="text-slate-500 block text-[11px] font-medium">Cryptographic Verification Token:</span>
                  <span className="text-slate-400 font-mono block select-all">
                    {log.receipt_id || "N/A"}
                  </span>
                </div>
              </div>

              {/* Policy violation console terminal logs */}
              <div className="bg-[#030712]/90 border border-red-950/55 rounded-lg p-4 font-mono text-[11px] text-red-400/90 leading-relaxed space-y-1.5">
                <div className="flex items-center gap-1.5 font-bold">
                  <span>&gt;_</span>
                  <span>Policy Violation Details:</span>
                </div>
                <div className="pl-4 text-red-300/80 leading-normal">
                  {log.details}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 text-xs text-slate-500 font-mono">
          No policy violations or scope exceptions detected in the current orchestration.
        </div>
      )}
    </div>
  );
}
