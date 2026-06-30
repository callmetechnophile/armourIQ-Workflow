import React, { useState } from "react";
import { GitBranch, GitCommit, Copy, RotateCcw, AlertTriangle } from "lucide-react";

interface Version {
  version_num: number;
  modified_by: string;
  change_summary: string;
  timestamp: string;
}

interface VersionHistoryProps {
  versionData?: {
    project_id: string;
    versions: Version[];
  };
  apiBase: string;
  onRefresh?: () => void;
}

export default function VersionHistory({ versionData, apiBase, onRefresh }: VersionHistoryProps) {
  const versions = versionData?.versions || [];
  const projectId = versionData?.project_id || "BionicHand_System";
  
  const [selectedV1, setSelectedV1] = useState<number | null>(null);
  const [selectedV2, setSelectedV2] = useState<number | null>(null);
  const [compareResult, setCompareResult] = useState<any | null>(null);
  const [forkName, setForkName] = useState("");
  const [forkSuccess, setForkSuccess] = useState<string | null>(null);
  
  const handleCompare = async () => {
    if (selectedV1 === null || selectedV2 === null) return;
    try {
      const res = await fetch(`${apiBase}/api/versioning/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          v1: selectedV1,
          v2: selectedV2
        })
      });
      if (res.ok) {
        const diff = await res.json();
        setCompareResult(diff);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRollback = async (versionNum: number) => {
    if (!confirm(`Are you sure you want to rollback ${projectId} to version ${versionNum}?`)) return;
    try {
      const res = await fetch(`${apiBase}/api/versioning/rollback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          version_num: versionNum
        })
      });
      if (res.ok) {
        alert("Rollback successful! A new version has been saved.");
        if (onRefresh) onRefresh();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleFork = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forkName) return;
    try {
      const res = await fetch(`${apiBase}/api/versioning/fork`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          version_num: versions[0]?.version_num || 1,
          new_name: forkName,
          user_id: "user_fork"
        })
      });
      if (res.ok) {
        setForkSuccess(`Project successfully forked into "${forkName}"!`);
        setForkName("");
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-4">
      {/* Version Tree & History */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-6">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Version Control Tree</h3>
          </div>
        </div>

        {/* Fork form */}
        <form onSubmit={handleFork} className="bg-zinc-900/60 p-4 border border-zinc-850 rounded-lg space-y-3">
          <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
            <Copy className="w-3.5 h-3.5 text-cyan-400" /> Fork This Workspace
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="New-Forked-Project-Name"
              value={forkName}
              onChange={(e) => setForkName(e.target.value)}
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              className="bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold px-4 py-2 rounded transition-all"
            >
              Fork
            </button>
          </div>
          {forkSuccess && <div className="text-xs font-mono text-emerald-400">{forkSuccess}</div>}
        </form>

        {/* Version Tree Flow */}
        <div className="relative pl-6 space-y-6 border-l-2 border-zinc-800 ml-4 py-2">
          {versions.map((v, idx) => (
            <div key={v.version_num} className="relative group">
              {/* Node Dot */}
              <div className={`absolute -left-[31px] top-1 w-4 h-4 rounded-full border-2 border-zinc-950 flex items-center justify-center transition-all ${
                idx === 0 ? "bg-cyan-500 shadow-lg shadow-cyan-500/50" : "bg-zinc-800"
              }`}>
                <GitCommit className="w-2.5 h-2.5 text-black" />
              </div>
              
              <div className="p-3 bg-zinc-900/40 border border-zinc-850 hover:border-zinc-700 rounded-lg space-y-1.5 transition-all">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-mono font-bold text-slate-100 flex items-center gap-2">
                    v{v.version_num}
                    {idx === 0 && <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-1.5 rounded">LATEST</span>}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleRollback(v.version_num)}
                      className="p-1 hover:bg-zinc-800 text-slate-400 hover:text-amber-400 rounded transition-all"
                      title="Rollback to this version"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                    <input
                      type="checkbox"
                      checked={selectedV1 === v.version_num || selectedV2 === v.version_num}
                      onChange={(e) => {
                        if (e.target.checked) {
                          if (selectedV1 === null) setSelectedV1(v.version_num);
                          else if (selectedV2 === null) setSelectedV2(v.version_num);
                        } else {
                          if (selectedV1 === v.version_num) setSelectedV1(null);
                          if (selectedV2 === v.version_num) setSelectedV2(null);
                        }
                      }}
                      className="w-3.5 h-3.5 accent-cyan-500 rounded"
                    />
                  </div>
                </div>
                <p className="text-xs font-mono text-slate-300">{v.change_summary}</p>
                <div className="flex justify-between items-center text-[9px] font-mono text-slate-500">
                  <span>Author: {v.modified_by}</span>
                  <span>{new Date(v.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Compare Panel */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-6">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Version Compare</h3>
          </div>
        </div>

        <div className="flex items-center justify-between gap-4 bg-zinc-900/60 p-4 border border-zinc-850 rounded-lg">
          <div className="text-xs font-mono text-slate-300">
            Selected: <span className="font-extrabold text-cyan-400">v{selectedV1 ?? "—"}</span> vs{" "}
            <span className="font-extrabold text-purple-400">v{selectedV2 ?? "—"}</span>
          </div>
          <button
            onClick={handleCompare}
            disabled={selectedV1 === null || selectedV2 === null}
            className="bg-purple-600 hover:bg-purple-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-white font-mono text-xs font-bold px-4 py-2 rounded transition-all"
          >
            Compare
          </button>
        </div>

        {/* Compare Results Display */}
        {compareResult ? (
          <div className="space-y-4 max-h-[400px] overflow-y-auto pr-1">
            {/* BOM Diffs */}
            <div className="space-y-2">
              <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest border-b border-zinc-900 pb-1">
                BOM Changes
              </div>
              {compareResult.bom_diff.added.map((item: any, idx: number) => (
                <div key={idx} className="p-2 border border-emerald-800/40 bg-emerald-950/15 rounded text-xs font-mono text-emerald-400">
                  + Added component: {item.component} ({item.selected_vendor})
                </div>
              ))}
              {compareResult.bom_diff.removed.map((item: any, idx: number) => (
                <div key={idx} className="p-2 border border-red-800/40 bg-red-950/15 rounded text-xs font-mono text-red-400">
                  - Removed component: {item.component}
                </div>
              ))}
              {compareResult.bom_diff.updated.map((item: any, idx: number) => (
                <div key={idx} className="p-2 border border-amber-800/40 bg-amber-950/15 rounded text-xs font-mono text-amber-400 space-y-1">
                  <div>* Updated component: {item.name}</div>
                  <div className="text-[10px] text-slate-400 pl-3">
                    Cost: ₹{item.old_cost} → ₹{item.new_cost} | Vendor: {item.old_vendor} → {item.new_vendor}
                  </div>
                </div>
              ))}
              {compareResult.bom_diff.added.length === 0 && compareResult.bom_diff.removed.length === 0 && compareResult.bom_diff.updated.length === 0 && (
                <div className="text-xs font-mono text-slate-500 italic">No component changes.</div>
              )}
            </div>

            {/* Wiring Diffs */}
            <div className="space-y-2">
              <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest border-b border-zinc-900 pb-1">
                Wiring Connections
              </div>
              {compareResult.wiring_diff.added.map((item: any, idx: number) => (
                <div key={idx} className="p-2 border border-emerald-800/40 bg-emerald-950/15 rounded text-xs font-mono text-emerald-400">
                  + Connected: {item.source}:{item.source_pin} → {item.target}:{item.target_pin}
                </div>
              ))}
              {compareResult.wiring_diff.removed.map((item: any, idx: number) => (
                <div key={idx} className="p-2 border border-red-800/40 bg-red-950/15 rounded text-xs font-mono text-red-400">
                  - Disconnected: {item.source} → {item.target}
                </div>
              ))}
              {compareResult.wiring_diff.added.length === 0 && compareResult.wiring_diff.removed.length === 0 && (
                <div className="text-xs font-mono text-slate-500 italic">No wiring changes.</div>
              )}
            </div>

            {/* Code Diff status */}
            <div className="space-y-2">
              <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest border-b border-zinc-900 pb-1">
                Firmware
              </div>
              <div className="p-2 bg-zinc-900/40 border border-zinc-850 rounded text-xs font-mono text-slate-300">
                {compareResult.code_differs ? "⚠ Firmware has changed between versions." : "Firmware matches exactly."}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 bg-zinc-900/10 border border-dashed border-zinc-800 rounded-lg text-center space-y-2">
            <AlertTriangle className="w-8 h-8 text-zinc-600" />
            <div className="text-xs font-mono text-slate-400">Select two checkboxed version nodes to execute comparison.</div>
          </div>
        )}
      </div>
    </div>
  );
}
