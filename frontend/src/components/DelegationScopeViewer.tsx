'use client';

import React, { useState } from 'react';
import { GitFork, ChevronDown, ChevronUp, Shield } from 'lucide-react';

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

interface DelegationScopeViewerProps {
  logs: AuditLog[];
}

export default function DelegationScopeViewer({ logs }: DelegationScopeViewerProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Extract delegations from audit logs
  const delegations = logs
    .filter((log) => log.action === "DELEGATION")
    .map((log) => {
      // Parse parent from details, e.g., "Delegated from Planner Agent to Research Agent"
      let parent = "Planner Agent";
      const match = log.details.match(/Delegated from (.*?) to/);
      if (match && match[1]) {
        parent = match[1];
      }
      return {
        parent,
        child: log.agent,
        allowedScope: log.allowed_scope,
        status: log.status === "SUCCESS" ? "ACTIVE" : log.status
      };
    });

  return (
    <div className="glass-panel border border-cyan-500/20 bg-slate-900/10">
      <div 
        className="flex justify-between items-center p-5 border-b border-slate-800/80 cursor-pointer select-none"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center gap-2.5">
          <GitFork className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Delegation Scope Viewer
          </h3>
        </div>
        <button className="text-slate-400 hover:text-white transition-all">
          {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </button>
      </div>

      {!isCollapsed && (
        <div className="p-5 overflow-x-auto">
          {delegations.length === 0 ? (
            <div className="text-center py-6 text-xs text-slate-500 font-mono">
              [SYSTEM NOTICE]: No delegations active. Submit a search query to initiate delegation.
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-widest text-[9px]">
                  <th className="py-2.5 px-3">Parent Agent</th>
                  <th className="py-2.5 px-3">Child Agent</th>
                  <th className="py-2.5 px-3">Allowed Scope</th>
                  <th className="py-2.5 px-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/30">
                {delegations.map((del, idx) => (
                  <tr key={`del-${idx}`} className="hover:bg-cyan-500/5 transition-all">
                    <td className="py-3.5 px-3 text-slate-400">{del.parent}</td>
                    <td className="py-3.5 px-3 font-semibold text-cyan-300">➔ {del.child}</td>
                    <td className="py-3.5 px-3">
                      <div className="flex flex-wrap gap-1.5">
                        {del.allowedScope.map((scope, i) => (
                          <span 
                            key={i} 
                            className="text-[9px] bg-slate-950 border border-slate-800 text-cyan-400 px-2 py-0.5 rounded-full"
                          >
                            {scope}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-3 text-right">
                      <span className={`inline-flex items-center gap-1 text-[9px] font-extrabold px-2.5 py-0.5 rounded border ${
                        del.status === "ACTIVE" 
                          ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-400"
                          : "bg-red-950/20 border-red-500/30 text-red-400"
                      }`}>
                        <Shield className="w-3 h-3" />
                        {del.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
