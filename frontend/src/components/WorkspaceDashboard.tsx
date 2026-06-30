'use client';

import React, { useState, useEffect } from 'react';
import { Database, Folder, Plus, Trash2, Copy, History, Download, RefreshCw } from 'lucide-react';

interface SavedProject {
  id: number;
  name: string;
  prompt: string;
  version: number;
  timestamp: string;
}

interface ProjectVersion {
  id: number;
  name: string;
  version: number;
  prompt: string;
  timestamp: string;
}

interface WorkspaceDashboardProps {
  activeProjectName: string;
  currentData: any; // Entire active pipeline output payload
  onLoadProject: (data: any) => void;
  onSaveTrigger: (name: string) => Promise<void>;
}

export default function WorkspaceDashboard({ 
  activeProjectName, 
  currentData, 
  onLoadProject,
  onSaveTrigger 
}: WorkspaceDashboardProps) {
  const [projects, setProjects] = useState<SavedProject[]>([]);
  const [versions, setVersions] = useState<ProjectVersion[]>([]);
  const [selectedProjectName, setSelectedProjectName] = useState<string | null>(null);
  const [saveName, setSaveName] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [msg, setMsg] = useState<{ text: string; isError: boolean } | null>(null);

  // Fetch saved projects
  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/workspace/list");
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
      }
    } catch (err) {
      console.error(err);
      setMsg({ text: "Failed to load projects list from database.", isError: true });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
    if (activeProjectName) {
      setSaveName(activeProjectName);
      setSelectedProjectName(activeProjectName);
      fetchVersions(activeProjectName);
    }
  }, [activeProjectName]);

  const fetchVersions = async (name: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/workspace/versions/${encodeURIComponent(name)}`);
      if (res.ok) {
        const data = await res.json();
        setVersions(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSave = async () => {
    if (!saveName.trim() || !currentData) return;
    setIsLoading(true);
    setMsg(null);
    try {
      const payload = {
        name: saveName.trim(),
        prompt: currentData.intent || "Bionic robotic hand",
        bom: currentData.components || [],
        power_analysis: currentData.power_analysis || {},
        dependency_graph: currentData.dependency_graph || {},
        wiring_diagram: currentData.wiring_diagram || {},
        papers: currentData.papers || [],
        gantt: currentData.gantt || [],
        code: currentData.code || {},
        exports: currentData.exports || {}
      };
      
      const res = await fetch("http://localhost:8000/api/workspace/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        setMsg({ text: `Workspace saved as '${saveName}' version!`, isError: false });
        fetchProjects();
        fetchVersions(saveName.trim());
        setSelectedProjectName(saveName.trim());
      } else {
        setMsg({ text: "Failed to save project version.", isError: true });
      }
    } catch (err) {
      console.error(err);
      setMsg({ text: "Database network failure.", isError: true });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoad = async (versionId: number) => {
    setIsLoading(true);
    setMsg(null);
    try {
      const res = await fetch(`http://localhost:8000/api/workspace/load/${versionId}`);
      if (res.ok) {
        const data = await res.json();
        onLoadProject(data);
        setMsg({ text: `Loaded version ${data.version} of project successfully!`, isError: false });
      } else {
        setMsg({ text: "Failed to load project details.", isError: true });
      }
    } catch (err) {
      console.error(err);
      setMsg({ text: "Database load network failure.", isError: true });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClone = async (versionId: number) => {
    const cloneName = prompt("Enter new name for cloned project:");
    if (!cloneName || !cloneName.trim()) return;
    
    setIsLoading(true);
    setMsg(null);
    try {
      const res = await fetch("http://localhost:8000/api/workspace/clone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: versionId,
          new_name: cloneName.trim()
        })
      });
      if (res.ok) {
        setMsg({ text: `Project cloned successfully as '${cloneName.trim()}'!`, isError: false });
        fetchProjects();
      } else {
        setMsg({ text: "Failed to clone project.", isError: true });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (versionId: number, name: string) => {
    if (!confirm("Are you sure you want to delete this version?")) return;
    setIsLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/workspace/delete/${versionId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        setMsg({ text: "Project version deleted successfully.", isError: false });
        fetchProjects();
        if (selectedProjectName === name) {
          fetchVersions(name);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProjectSelect = (name: string) => {
    setSelectedProjectName(name);
    setSaveName(name);
    fetchVersions(name);
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Messages */}
      {msg && (
        <div className={`p-3 rounded border text-xs ${
          msg.isError ? "border-red-500/20 bg-red-950/20 text-red-300" : "border-emerald-500/20 bg-emerald-950/20 text-emerald-300"
        }`}>
          {msg.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Projects list & Save project */}
        <div className="lg:col-span-1 space-y-6">
          {/* Save Active Workspace */}
          <div className="glass-panel p-5 border border-blue-500/20 bg-zinc-950/40 space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <Database className="w-4 h-4 text-cyan-400" />
              Save Workspace
            </h3>
            <p className="text-[10px] text-slate-400 leading-normal">
              Store components, schematics, power warnings, research ranking, and code.
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={saveName}
                onChange={(e) => setSaveName(e.target.value)}
                placeholder="Workspace Project Name"
                className="flex-1 bg-slate-950 border border-slate-800 text-xs px-3 py-2 rounded text-slate-200 outline-none focus:border-cyan-800"
              />
              <button
                onClick={handleSave}
                disabled={isLoading || !saveName.trim() || !currentData}
                className="bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-400 px-3 rounded text-xs font-bold transition-all cursor-pointer disabled:opacity-40"
              >
                Save
              </button>
            </div>
          </div>

          {/* Saved Projects Dashboard */}
          <div className="glass-panel p-5 border border-blue-500/20 bg-zinc-950/40 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                <Folder className="w-4 h-4 text-cyan-400" />
                Saved Projects
              </h3>
              <button onClick={fetchProjects} className="text-slate-400 hover:text-slate-200 cursor-pointer">
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
            
            {isLoading && projects.length === 0 ? (
              <div className="text-center py-4 text-slate-500 text-xs animate-pulse">Loading saved projects...</div>
            ) : projects.length === 0 ? (
              <div className="text-center py-6 border border-slate-900 border-dashed rounded text-xs text-slate-500 italic">
                No projects saved to DB workspace.
              </div>
            ) : (
              <div className="space-y-2 max-h-[260px] overflow-y-auto">
                {projects.map((proj) => (
                  <div
                    key={proj.id}
                    onClick={() => handleProjectSelect(proj.name)}
                    className={`p-3 rounded border text-left cursor-pointer transition-all ${
                      selectedProjectName === proj.name
                        ? "bg-cyan-950/20 border-cyan-500/40 text-cyan-400"
                        : "bg-slate-900/10 border-slate-900 hover:border-slate-800 text-slate-300"
                    }`}
                  >
                    <div className="text-xs font-bold">{proj.name}</div>
                    <div className="text-[9px] text-slate-500 mt-1">
                      Latest: v{proj.version} • {new Date(proj.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right columns: Version history details & Version operations */}
        <div className="lg:col-span-2">
          <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40 h-full space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <History className="w-4 h-4 text-cyan-400" />
              Version Release History {selectedProjectName ? `[${selectedProjectName}]` : ""}
            </h3>

            {!selectedProjectName ? (
              <div className="flex flex-col items-center justify-center h-[280px] border border-slate-900 border-dashed rounded text-xs text-slate-500 italic">
                Select a project on the left to inspect its version repository.
              </div>
            ) : versions.length === 0 ? (
              <div className="text-center py-6 text-slate-500 text-xs">Loading versions...</div>
            ) : (
              <div className="space-y-3 overflow-y-auto max-h-[360px] pr-2">
                {versions.map((ver) => (
                  <div
                    key={ver.id}
                    className="p-4 bg-slate-900/10 border border-slate-800 hover:border-slate-700 rounded-lg flex items-center justify-between gap-4 transition-all"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs bg-slate-950 border border-slate-800 text-cyan-400 px-2 py-0.5 rounded font-bold">
                          Version {ver.version}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {new Date(ver.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-300">
                        Query Prompt: "{ver.prompt}"
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <button
                        onClick={() => handleLoad(ver.id)}
                        title="Load Project"
                        className="text-[10px] bg-cyan-950/40 border border-cyan-800 hover:bg-cyan-900/40 px-2.5 py-1.5 rounded transition-all text-cyan-400 font-bold cursor-pointer flex items-center gap-1"
                      >
                        <Download className="w-3 h-3" />
                        Load
                      </button>
                      <button
                        onClick={() => handleClone(ver.id)}
                        title="Duplicate Project"
                        className="text-[10px] border border-slate-800 bg-slate-900/60 hover:bg-slate-800 px-2.5 py-1.5 rounded transition-all text-slate-300 cursor-pointer flex items-center gap-1"
                      >
                        <Copy className="w-3 h-3" />
                        Clone
                      </button>
                      <button
                        onClick={() => handleDelete(ver.id, ver.name)}
                        title="Delete Version"
                        className="text-[10px] border border-red-950/60 bg-red-950/10 hover:bg-red-900/30 px-2.5 py-1.5 rounded transition-all text-red-400 cursor-pointer flex items-center gap-1"
                      >
                        <Trash2 className="w-3 h-3" />
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
